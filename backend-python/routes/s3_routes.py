from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from services.minio_service import minio_service
from services.dask_service import dask_service

router = APIRouter(prefix="/api/s3", tags=["s3"])


class S3QueryRequest(BaseModel):
    bucket: str
    path: str
    query: Optional[str] = None
    limit: int = 1000


class RawSQLRequest(BaseModel):
    query: str


# File Browser Endpoints

@router.get("/buckets")
async def list_buckets():
    """List all S3 buckets."""
    try:
        buckets = minio_service.list_buckets()
        return {"success": True, "data": buckets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/buckets/{bucket_name}")
async def create_bucket(bucket_name: str):
    """Create a new bucket."""
    try:
        created = minio_service.create_bucket(bucket_name)
        return {
            "success": True,
            "created": created,
            "message": "Bucket created" if created else "Bucket already exists"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/browse/{bucket}")
async def browse_bucket(
    bucket: str,
    prefix: str = "",
    recursive: bool = False
):
    """Browse files and folders in bucket."""
    try:
        objects = minio_service.list_objects(bucket, prefix, recursive)
        return {"success": True, "data": objects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{bucket}/{path:path}")
async def get_file_info(bucket: str, path: str):
    """Get file information."""
    try:
        info = minio_service.get_object_info(bucket, path)
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/upload/{bucket}")
async def upload_file(
    bucket: str,
    prefix: str = "",
    file: UploadFile = File(...)
):
    """Upload file to bucket."""
    try:
        # Ensure bucket exists
        if not minio_service.bucket_exists(bucket):
            minio_service.create_bucket(bucket)

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Upload to MinIO
        object_name = f"{prefix}{file.filename}" if prefix else file.filename
        minio_service.upload_file(
            bucket,
            object_name,
            tmp_path,
            file.content_type
        )

        # Cleanup
        os.unlink(tmp_path)

        return {"success": True, "path": object_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file/{bucket}/{path:path}")
async def delete_file(bucket: str, path: str):
    """Delete file from bucket."""
    try:
        minio_service.delete_object(bucket, path)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-url/{bucket}/{path:path}")
async def get_download_url(bucket: str, path: str, expires: int = 3600):
    """Get presigned download URL."""
    try:
        url = minio_service.get_presigned_url(bucket, path, expires)
        return {"success": True, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Query Endpoints

@router.post("/query")
async def query_s3_file(request: S3QueryRequest):
    """Execute query on S3 file using Dask."""
    try:
        result = dask_service.query_s3_file(
            request.bucket,
            request.path,
            request.query,
            request.limit
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/sql")
async def execute_raw_sql(request: RawSQLRequest):
    """Execute raw SQL query (for advanced users)."""
    try:
        result = duckdb_service.execute_query(request.query)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/{bucket}/{path:path}")
async def get_file_schema(bucket: str, path: str):
    """Get schema of S3 file."""
    try:
        result = dask_service.get_schema(bucket, path)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{bucket}/{path:path}")
async def preview_file(bucket: str, path: str, limit: int = Query(default=100, le=1000)):
    """Preview file contents."""
    try:
        result = dask_service.preview_file(bucket, path, limit)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def s3_health():
    """Check S3/MinIO connection health."""
    try:
        is_connected = minio_service.test_connection()
        return {
            "success": True,
            "minio": "connected" if is_connected else "disconnected"
        }
    except Exception as e:
        return {
            "success": False,
            "minio": "disconnected",
            "error": str(e)
        }
