import sys
import os
from dotenv import load_dotenv

# Load .env FIRST before any other imports
load_dotenv()

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
load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"=== Configuration Loaded ===")
    print(f"MinIO Endpoint: {settings.minio_endpoint}")
    print(f"MinIO Access Key: {settings.minio_access_key}")
    print(f"MinIO Secure: {settings.minio_secure}")
    print(f"MinIO Bucket: {settings.minio_bucket}")
    print(f"ClickHouse Host: {settings.clickhouse_host}:{settings.clickhouse_port}")
    print(f"PostgreSQL Host: {settings.postgres_host}:{settings.postgres_port}")
    print(f"===========================")
    
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
