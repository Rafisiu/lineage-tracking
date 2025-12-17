import asyncio
import json
import time
from datetime import datetime
from typing import Optional
from config.database import settings
from models.schema import FieldMapping, DatabaseConnection
from models.migration import (
    MigrationRequest,
    MigrationStatus,
    MigrationProgress,
    MigrationStatusResponse
)
from services.postgres_service import postgres_service
from services.clickhouse_service import clickhouse_service
from services.history_service import history_service
from services.mapping_service import mapping_service


class MigrationService:
    def __init__(self):
        self._active_migrations: dict[str, MigrationStatusResponse] = {}

    async def execute_migration(self, request: MigrationRequest) -> str:
        """Start migration process and return migration ID."""
        # Validate mappings
        mappings = [FieldMapping(**m) if isinstance(m, dict) else m for m in request.mappings]
        validation = mapping_service.validate_mappings(mappings)

        if not validation["valid"]:
            raise ValueError(f"Invalid mappings: {', '.join(validation['errors'])}")

        # Get active mappings
        active_mappings = [m for m in mappings if not m.skip]
        source_columns = [m.source_field for m in active_mappings]
        destination_fields = [m.destination_field for m in active_mappings]

        # Build source connection string
        conn = request.source_connection
        if conn:
            source_str = f"postgres://{conn.host}:{conn.port}/{conn.database}"
        else:
            source_str = f"postgres://{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

        # Create migration history record
        migration_id = history_service.create_migration_record(
            source=source_str,
            destination=request.destination_table,
            source_table=request.source_table,
            description=request.description,
            fields=source_columns,
            mappings=[m.model_dump() for m in active_mappings],
            created_by=request.created_by
        )

        # Initialize status tracking
        self._active_migrations[migration_id] = MigrationStatusResponse(
            id=migration_id,
            status=MigrationStatus.RUNNING,
            progress=MigrationProgress(
                total_records=0,
                processed_records=0,
                percentage=0.0
            ),
            started_at=datetime.utcnow()
        )

        # Start async migration
        asyncio.create_task(
            self._perform_migration(
                migration_id,
                request,
                active_mappings,
                source_columns,
                destination_fields
            )
        )

        return migration_id

    def get_migration_status(self, migration_id: str) -> Optional[MigrationStatusResponse]:
        """Get status of active migration."""
        return self._active_migrations.get(migration_id)

    async def _perform_migration(
        self,
        migration_id: str,
        request: MigrationRequest,
        mappings: list[FieldMapping],
        source_columns: list[str],
        destination_fields: list[str]
    ) -> None:
        """Perform the actual migration."""
        start_time = time.time()
        records_migrated = 0

        try:
            # Create table if requested
            if request.create_table:
                ddl = mapping_service.generate_ddl_from_mappings(
                    request.destination_table,
                    mappings
                )
                clickhouse_service.create_table(ddl)

            # Get total row count
            schema = await postgres_service.get_table_schema(
                request.source_table,
                request.source_schema,
                request.source_connection
            )
            total_records = schema.row_count or 0

            # Update progress
            status = self._active_migrations[migration_id]
            status.progress.total_records = total_records

            # Migrate in batches
            offset = 0
            batch_num = 0
            total_batches = (total_records + request.batch_size - 1) // request.batch_size if total_records > 0 else 1

            while True:
                # Extract batch
                data = await postgres_service.extract_data(
                    request.source_table,
                    request.source_schema,
                    source_columns,
                    offset,
                    request.batch_size,
                    request.source_connection
                )

                if not data:
                    break

                # Transform data
                transformed = self._transform_data(data, mappings)

                # Insert into ClickHouse
                inserted = clickhouse_service.insert_data(
                    request.destination_table,
                    transformed,
                    destination_fields
                )

                records_migrated += inserted
                batch_num += 1
                offset += request.batch_size

                # Update progress
                percentage = (records_migrated / total_records * 100) if total_records > 0 else 100
                status.progress.processed_records = records_migrated
                status.progress.percentage = round(percentage, 2)
                status.progress.current_batch = batch_num
                status.progress.total_batches = total_batches

            # Complete migration
            duration = int(time.time() - start_time)
            history_service.update_migration_status(
                migration_id,
                MigrationStatus.COMPLETED,
                records_migrated,
                duration
            )

            status.status = MigrationStatus.COMPLETED
            status.completed_at = datetime.utcnow()
            status.progress.percentage = 100.0

        except Exception as e:
            duration = int(time.time() - start_time)
            error_message = str(e)

            history_service.update_migration_status(
                migration_id,
                MigrationStatus.FAILED,
                records_migrated,
                duration,
                error_message
            )

            if migration_id in self._active_migrations:
                status = self._active_migrations[migration_id]
                status.status = MigrationStatus.FAILED
                status.error_message = error_message
                status.completed_at = datetime.utcnow()

    def _transform_data(
        self,
        data: list[dict],
        mappings: list[FieldMapping]
    ) -> list[dict]:
        """Transform data according to field mappings."""
        transformed = []

        for record in data:
            new_record = {}

            for mapping in mappings:
                value = record.get(mapping.source_field)

                # Handle null values
                if value is None:
                    # Set defaults for non-nullable types
                    dest_type = mapping.destination_type.lower()
                    if "nullable" not in dest_type:
                        if "int" in dest_type or "uint" in dest_type:
                            value = 0
                        elif "float" in dest_type or "decimal" in dest_type:
                            value = 0.0
                        elif "string" in dest_type:
                            value = ""
                        elif "array" in dest_type:
                            value = []

                # Handle boolean to UInt8
                if isinstance(value, bool):
                    value = 1 if value else 0

                # Handle arrays (convert to JSON string if needed)
                if isinstance(value, (list, dict)):
                    if "array" not in mapping.destination_type.lower():
                        value = json.dumps(value)

                new_record[mapping.destination_field] = value

            transformed.append(new_record)

        return transformed


# Singleton instance
migration_service = MigrationService()
