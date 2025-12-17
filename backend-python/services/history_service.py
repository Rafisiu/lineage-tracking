import uuid
import json
from typing import Optional
from datetime import datetime
from services.clickhouse_service import clickhouse_service
from models.migration import MigrationStatus, MigrationHistory


class HistoryService:
    def __init__(self):
        self._clickhouse = clickhouse_service

    def create_migration_record(
        self,
        source: str,
        destination: str,
        source_table: str,
        description: str,
        fields: list[str],
        mappings: list[dict],
        created_by: str
    ) -> str:
        """Create a new migration history record."""
        migration_id = str(uuid.uuid4())

        # Escape strings for SQL
        def escape(s: str) -> str:
            return s.replace("\\", "\\\\").replace("'", "\\'")

        fields_str = ", ".join([f"'{escape(f)}'" for f in fields])
        mappings_json = json.dumps(mappings).replace("\\", "\\\\").replace("'", "\\'")

        query = f"""
        INSERT INTO migration_history (
            id, source, destination, source_table, deskripsi,
            tabel_fields, field_mappings, status, records_migrated,
            duration_seconds, created_by, metadata
        ) VALUES (
            '{migration_id}',
            '{escape(source)}',
            '{escape(destination)}',
            '{escape(source_table)}',
            '{escape(description)}',
            [{fields_str}],
            '{mappings_json}',
            'running',
            0,
            0,
            '{escape(created_by)}',
            '{{}}'
        )
        """

        self._clickhouse.execute_query(query)
        return migration_id

    def update_migration_status(
        self,
        migration_id: str,
        status: MigrationStatus,
        records_migrated: int,
        duration_seconds: int,
        error_message: Optional[str] = None
    ) -> None:
        """Update migration record status."""
        error_part = f", error_message = '{error_message}'" if error_message else ""

        query = f"""
        ALTER TABLE migration_history
        UPDATE
            status = '{status.value}',
            records_migrated = {records_migrated},
            duration_seconds = {duration_seconds}
            {error_part}
        WHERE id = '{migration_id}'
        """

        self._clickhouse.execute_query(query)

    def get_migration_history(
        self,
        limit: int = 20,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> dict:
        """Get migration history with pagination."""
        where_clause = f"WHERE status = '{status_filter}'" if status_filter else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM migration_history {where_clause}"
        count_result = self._clickhouse.execute_query(count_query)
        total = count_result["data"][0]["total"] if count_result["data"] else 0

        # Get records
        query = f"""
        SELECT * FROM migration_history
        {where_clause}
        ORDER BY migration_time DESC
        LIMIT {limit} OFFSET {offset}
        """

        result = self._clickhouse.execute_query(query)

        return {
            "total": total,
            "migrations": result["data"]
        }

    def get_migration_by_id(self, migration_id: str) -> Optional[dict]:
        """Get specific migration by ID."""
        query = f"SELECT * FROM migration_history WHERE id = '{migration_id}'"
        result = self._clickhouse.execute_query(query)

        if result["data"]:
            return result["data"][0]
        return None


# Singleton instance
history_service = HistoryService()
