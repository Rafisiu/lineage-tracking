import clickhouse_connect
from typing import Optional, Any
import time
import json
from config.database import settings


class ClickHouseService:
    def __init__(self):
        self._client = None

    def _get_client(self):
        """Get or create ClickHouse client."""
        if self._client is None:
            self._client = clickhouse_connect.get_client(
                host=settings.clickhouse_host,
                port=settings.clickhouse_port,
                username=settings.clickhouse_user,
                password=settings.clickhouse_password,
                database=settings.clickhouse_database
            )
        return self._client

    def execute_query(self, query: str, format: str = "JSON") -> dict:
        """Execute query and return results."""
        client = self._get_client()
        start_time = time.time()

        query_upper = query.strip().upper()

        if query_upper.startswith("SELECT") or query_upper.startswith("SHOW") or query_upper.startswith("DESCRIBE"):
            result = client.query(query)
            execution_time = (time.time() - start_time) * 1000

            # Convert to list of dicts
            columns = result.column_names
            data = [dict(zip(columns, row)) for row in result.result_rows]

            return {
                "success": True,
                "data": data,
                "rows": len(data),
                "execution_time_ms": round(execution_time, 2),
                "metadata": {"columns": columns}
            }
        else:
            client.command(query)
            execution_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "data": [],
                "rows": 0,
                "execution_time_ms": round(execution_time, 2),
                "metadata": {}
            }

    def create_table(self, ddl: str) -> None:
        """Create table using DDL."""
        client = self._get_client()
        client.command(ddl)

    def insert_data(self, table_name: str, data: list[dict], columns: list[str]) -> int:
        """Insert data into table."""
        if not data:
            return 0

        client = self._get_client()

        # Convert list of dicts to list of tuples
        rows = []
        for record in data:
            row = tuple(record.get(col) for col in columns)
            rows.append(row)

        client.insert(table_name, rows, column_names=columns)
        return len(rows)

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        client = self._get_client()
        result = client.command(f"EXISTS TABLE {table_name}")
        return result == 1

    def get_table_info(self, table_name: str) -> list[dict]:
        """Get table schema information."""
        client = self._get_client()
        result = client.query(f"DESCRIBE TABLE {table_name}")
        columns = result.column_names
        return [dict(zip(columns, row)) for row in result.result_rows]

    def initialize_migration_history_table(self) -> None:
        """Create migration_history table if not exists."""
        ddl = """
        CREATE TABLE IF NOT EXISTS migration_history (
            id UUID DEFAULT generateUUIDv4(),
            source String,
            destination String,
            source_table String,
            migration_time DateTime DEFAULT now(),
            deskripsi String,
            tabel_fields Array(String),
            field_mappings String,
            status Enum8('pending' = 1, 'running' = 2, 'completed' = 3, 'failed' = 4),
            records_migrated UInt64,
            error_message Nullable(String),
            duration_seconds UInt32,
            created_by String,
            metadata String
        ) ENGINE = MergeTree()
        ORDER BY (migration_time, id)
        PARTITION BY toYYYYMM(migration_time)
        """
        self.create_table(ddl)

    def ping(self) -> bool:
        """Test ClickHouse connection."""
        try:
            client = self._get_client()
            client.ping()
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Close client connection."""
        if self._client:
            self._client.close()
            self._client = None


# Singleton instance
clickhouse_service = ClickHouseService()
