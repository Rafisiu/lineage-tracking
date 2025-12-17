import re
from models.schema import TableSchema, FieldMapping
from utils.type_mapper import map_postgres_to_clickhouse, validate_type_mapping


class MappingService:
    def generate_mappings(
        self,
        source_schema: TableSchema,
        destination_table: str
    ) -> dict:
        """Generate field mappings from source schema."""
        mappings = []
        warnings = []

        for column in source_schema.columns:
            # Validate type mapping
            validation = validate_type_mapping(column.type)

            if validation.get("warning"):
                warnings.append(f"{column.name}: {validation['warning']}")

            # Get ClickHouse type
            ch_type = map_postgres_to_clickhouse(
                column.type,
                nullable=column.nullable and not column.primary_key
            )

            mapping = FieldMapping(
                source_field=column.name,
                source_type=column.type,
                destination_field=column.name,
                destination_type=ch_type,
                transformation=None,
                skip=False
            )

            mappings.append(mapping)

        # Generate DDL
        suggested_ddl = self.generate_ddl_from_mappings(destination_table, mappings)

        return {
            "mappings": [m.model_dump() for m in mappings],
            "suggested_ddl": suggested_ddl,
            "warnings": warnings
        }

    def validate_mappings(self, mappings: list[FieldMapping]) -> dict:
        """Validate field mappings."""
        errors = []

        # Check for duplicate destination fields
        dest_fields = [m.destination_field for m in mappings if not m.skip]
        duplicates = set([f for f in dest_fields if dest_fields.count(f) > 1])
        if duplicates:
            errors.append(f"Duplicate destination fields: {', '.join(duplicates)}")

        # Check at least one field is not skipped
        active_fields = [m for m in mappings if not m.skip]
        if not active_fields:
            errors.append("At least one field must not be skipped")

        # Validate field names
        field_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        for mapping in mappings:
            if not mapping.skip:
                if not field_pattern.match(mapping.destination_field):
                    errors.append(
                        f"Invalid destination field name: {mapping.destination_field}"
                    )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def generate_ddl_from_mappings(
        self,
        table_name: str,
        mappings: list[FieldMapping],
        engine: str = "MergeTree()",
        order_by: str = None
    ) -> str:
        """Generate CREATE TABLE DDL from field mappings."""
        active_mappings = [m for m in mappings if not m.skip]

        if not active_mappings:
            raise ValueError("No active mappings to generate DDL")

        # Build column definitions
        columns = []
        for mapping in active_mappings:
            columns.append(f"    {mapping.destination_field} {mapping.destination_type}")

        columns_str = ",\n".join(columns)

        # Determine ORDER BY
        if not order_by:
            order_by = active_mappings[0].destination_field

        ddl = f"""CREATE TABLE IF NOT EXISTS {table_name} (
{columns_str}
) ENGINE = {engine}
ORDER BY ({order_by})"""

        return ddl


# Singleton instance
mapping_service = MappingService()
