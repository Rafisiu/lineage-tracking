from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from models.schema import DatabaseConnection, TableSchema, ColumnDefinition, FieldMapping
from models.migration import MigrationRequest
from services.postgres_service import postgres_service
from services.clickhouse_service import clickhouse_service
from services.migration_service import migration_service
from services.history_service import history_service
from services.mapping_service import mapping_service

router = APIRouter(prefix="/api/migration", tags=["migration"])


class AnalyzeSourceRequest(BaseModel):
    table: str
    schema_name: str = "public"
    connection: Optional[DatabaseConnection] = None

    class Config:
        populate_by_name = True


class SuggestMappingRequest(BaseModel):
    source_schema: TableSchema
    destination_table: str


@router.post("/analyze-source")
async def analyze_source(request: AnalyzeSourceRequest):
    """Analyze source PostgreSQL table schema."""
    try:
        schema = await postgres_service.get_table_schema(
            request.table,
            request.schema_name,
            request.connection
        )

        return {
            "success": True,
            "data": {
                "table": schema.table,
                "schema": schema.schema_name,
                "columns": [col.model_dump() for col in schema.columns],
                "row_count": schema.row_count,
                "estimated_size_mb": schema.estimated_size_mb
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/suggest-mapping")
async def suggest_mapping(request: SuggestMappingRequest):
    """Generate field mappings and DDL suggestion."""
    try:
        result = mapping_service.generate_mappings(
            request.source_schema,
            request.destination_table
        )

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/execute")
async def execute_migration(request: MigrationRequest):
    """Start migration from PostgreSQL to ClickHouse."""
    try:
        migration_id = await migration_service.execute_migration(request)

        return {
            "success": True,
            "migration_id": migration_id,
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status/{migration_id}")
async def get_migration_status(migration_id: str):
    """Get status of a migration."""
    try:
        # Check active migrations first
        status = migration_service.get_migration_status(migration_id)

        if status:
            return {
                "success": True,
                "data": {
                    "id": status.id,
                    "status": status.status.value,
                    "progress": status.progress.model_dump() if status.progress else None,
                    "started_at": status.started_at.isoformat() if status.started_at else None,
                    "completed_at": status.completed_at.isoformat() if status.completed_at else None,
                    "error_message": status.error_message
                }
            }

        # Check history
        history = history_service.get_migration_by_id(migration_id)

        if history:
            return {
                "success": True,
                "data": {
                    "id": history["id"],
                    "status": history["status"],
                    "progress": {
                        "total_records": history["records_migrated"],
                        "processed_records": history["records_migrated"],
                        "percentage": 100.0
                    },
                    "started_at": str(history["migration_time"]),
                    "completed_at": None,
                    "error_message": history.get("error_message")
                }
            }

        raise HTTPException(status_code=404, detail="Migration not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
async def get_migration_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None)
):
    """Get migration history with pagination."""
    try:
        result = history_service.get_migration_history(limit, offset, status)

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tables")
async def get_tables(schema: str = Query(default="public")):
    """List tables in PostgreSQL schema."""
    try:
        tables = await postgres_service.get_tables(schema)

        return {
            "success": True,
            "data": tables
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
