import sys
import os

# Add backend-python to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from config.database import settings
from routes.query_routes import router as query_router
from routes.migration_routes import router as migration_router
from routes.s3_routes import router as s3_router
from routes.auth_routes import router as auth_router
from services.clickhouse_service import clickhouse_service
from services.postgres_service import postgres_service
from services.duckdb_service import duckdb_service
from dotenv import load_dotenv
load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    try:
        clickhouse_service.initialize_migration_history_table()
        print("Migration history table initialized")
    except Exception as e:
        print(f"Warning: Could not initialize migration history table: {e}")

    yield

    # Shutdown
    await postgres_service.close()
    clickhouse_service.close()
    duckdb_service.close()


app = FastAPI(
    title="ClickHouse Migration API",
    description="PostgreSQL to ClickHouse migration backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(query_router)
app.include_router(migration_router)
app.include_router(s3_router)


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
