from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.clickhouse_service import clickhouse_service

router = APIRouter(prefix="/api/query", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    format: str = "JSON"


@router.post("/execute")
async def execute_query(request: QueryRequest):
    """Execute ClickHouse query."""
    try:
        result = clickhouse_service.execute_query(request.query, request.format)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def health_check():
    """Check ClickHouse connection health."""
    try:
        is_connected = clickhouse_service.ping()
        return {
            "success": True,
            "clickhouse": "connected" if is_connected else "disconnected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
