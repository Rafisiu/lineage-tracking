import asyncpg
from typing import Optional
from config.database import settings
from models.schema import TableSchema, ColumnDefinition, DatabaseConnection


class PostgresService:
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self, connection: Optional[DatabaseConnection] = None) -> asyncpg.Pool:
        """Get or create connection pool."""
        if connection:
            return await asyncpg.create_pool(
                host=connection.host,
                port=connection.port,
                database=connection.database,
                user=connection.user,
                password=connection.password,
                min_size=1,
                max_size=10
            )

        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
                min_size=1,
                max_size=10
            )
        return self._pool

    async def test_connection(self, connection: Optional[DatabaseConnection] = None) -> bool:
        """Test PostgreSQL connection."""
        try:
            pool = await self._get_pool(connection)
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            if connection:
                await pool.close()
            return True
        except Exception:
            return False

    async def get_table_schema(
        self,
        table_name: str,
        schema: str = "public",
        connection: Optional[DatabaseConnection] = None
    ) -> TableSchema:
        """Get table schema from PostgreSQL."""
        pool = await self._get_pool(connection)

        try:
            async with pool.acquire() as conn:
                # Get column information
                columns_query = """
                    SELECT
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.column_default,
                        c.character_maximum_length,
                        CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key
                    FROM information_schema.columns c
                    LEFT JOIN (
                        SELECT ku.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage ku
                            ON tc.constraint_name = ku.constraint_name
                        WHERE tc.constraint_type = 'PRIMARY KEY'
                            AND tc.table_schema = $1
                            AND tc.table_name = $2
                    ) pk ON c.column_name = pk.column_name
                    WHERE c.table_schema = $1 AND c.table_name = $2
                    ORDER BY c.ordinal_position
                """

                rows = await conn.fetch(columns_query, schema, table_name)

                if not rows:
                    raise ValueError(f"Table {schema}.{table_name} not found")

                columns = [
                    ColumnDefinition(
                        name=row["column_name"],
                        type=row["data_type"],
                        nullable=row["is_nullable"] == "YES",
                        primary_key=row["is_primary_key"],
                        default_value=row["column_default"],
                        max_length=row["character_maximum_length"]
                    )
                    for row in rows
                ]

                # Get row count
                count_query = f'SELECT COUNT(*) FROM "{schema}"."{table_name}"'
                row_count = await conn.fetchval(count_query)

                # Get estimated size
                size_query = """
                    SELECT pg_total_relation_size($1) / 1024.0 / 1024.0 as size_mb
                """
                size_mb = await conn.fetchval(size_query, f"{schema}.{table_name}")

                return TableSchema(
                    table=table_name,
                    schema=schema,
                    columns=columns,
                    row_count=row_count,
                    estimated_size_mb=float(size_mb) if size_mb else 0.0
                )
        finally:
            if connection:
                await pool.close()

    async def extract_data(
        self,
        table_name: str,
        schema: str = "public",
        columns: Optional[list[str]] = None,
        offset: int = 0,
        limit: int = 10000,
        connection: Optional[DatabaseConnection] = None
    ) -> list[dict]:
        """Extract data from PostgreSQL table."""
        pool = await self._get_pool(connection)

        try:
            async with pool.acquire() as conn:
                cols = ", ".join([f'"{c}"' for c in columns]) if columns else "*"
                query = f'SELECT {cols} FROM "{schema}"."{table_name}" OFFSET {offset} LIMIT {limit}'

                rows = await conn.fetch(query)
                return [dict(row) for row in rows]
        finally:
            if connection:
                await pool.close()

    async def get_tables(
        self,
        schema: str = "public",
        connection: Optional[DatabaseConnection] = None
    ) -> list[str]:
        """Get list of tables in schema."""
        pool = await self._get_pool(connection)

        try:
            async with pool.acquire() as conn:
                query = """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = $1 AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """
                rows = await conn.fetch(query, schema)
                return [row["table_name"] for row in rows]
        finally:
            if connection:
                await pool.close()

    async def close(self):
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None


# Singleton instance
postgres_service = PostgresService()
