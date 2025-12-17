import duckdb
import time
from config.database import settings


class DuckDBService:
    def __init__(self):
        self._conn = None

    def _get_connection(self):
        """Get or create DuckDB connection."""
        if self._conn is None:
            self._conn = duckdb.connect()
            self._setup_s3()
        return self._conn

    def _setup_s3(self):
        """Configure S3/MinIO connection."""
        conn = self._conn
        conn.execute("INSTALL httpfs;")
        conn.execute("LOAD httpfs;")

        # DuckDB expects endpoint without protocol (it adds http:// internally)
        endpoint = settings.minio_endpoint.replace('http://', '').replace('https://', '')

        print(f"[DuckDB] Setting up S3 with endpoint: {endpoint}")
        conn.execute(f"SET s3_endpoint='{endpoint}';")
        conn.execute(f"SET s3_access_key_id='{settings.minio_access_key}';")
        conn.execute(f"SET s3_secret_access_key='{settings.minio_secret_key}';")
        conn.execute("SET s3_use_ssl=false;")
        conn.execute("SET s3_url_style='path';")

    def execute_query(self, query: str) -> dict:
        """Execute SQL query."""
        conn = self._get_connection()
        start_time = time.time()

        try:
            print(f"[DuckDB] Executing query: {query[:200]}...")  # Debug log
            result = conn.execute(query)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            execution_time = (time.time() - start_time) * 1000

            print(f"[DuckDB] Query successful: {len(rows)} rows in {round(execution_time, 2)}ms")
            return {
                "success": True,
                "columns": columns,
                "data": [dict(zip(columns, row)) for row in rows],
                "row_count": len(rows),
                "execution_time_ms": round(execution_time, 2)
            }
        except Exception as e:
            print(f"[DuckDB] Query failed: {str(e)}")  # Debug log
            return {
                "success": False,
                "error": str(e)
            }

    def query_s3_file(
        self,
        bucket: str,
        path: str,
        query: str = None,
        limit: int = 1000
    ) -> dict:
        """Query S3 file by downloading it temporarily."""
        import tempfile
        import os
        from services.minio_service import minio_service

        # Download file to temp location
        print(f"[DuckDB] Downloading s3://{bucket}/{path} from MinIO...")
        temp_file = None
        temp_path = None

        try:
            # Create temp file
            suffix = os.path.splitext(path)[1]  # Get file extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_path = temp_file.name
            temp_file.close()

            # Download from MinIO
            minio_service.download_file(bucket, path, temp_path)
            print(f"[DuckDB] Downloaded to {temp_path}")

            # Auto-detect format and build query
            if path.endswith('.parquet'):
                base_query = f"SELECT * FROM read_parquet('{temp_path}')"
            elif path.endswith('.csv') or path.endswith('.csv.gz'):
                base_query = f"SELECT * FROM read_csv_auto('{temp_path}')"
            elif path.endswith('.json') or path.endswith('.jsonl'):
                base_query = f"SELECT * FROM read_json_auto('{temp_path}')"
            else:
                return {"success": False, "error": f"Unsupported file format: {path}"}

            if query:
                # User provided custom query - wrap around base
                full_query = f"WITH data AS ({base_query}) {query}"
            else:
                full_query = f"{base_query} LIMIT {limit}"

            return self.execute_query(full_query)

        except Exception as e:
            print(f"[DuckDB] Error: {e}")
            return {"success": False, "error": str(e)}
        finally:
            # Cleanup temp file
            if temp_file and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    print(f"[DuckDB] Cleaned up temp file")
                except:
                    pass

    def get_schema(self, bucket: str, path: str) -> dict:
        """Get schema of S3 file."""
        s3_path = f"s3://{bucket}/{path}"

        if path.endswith('.parquet'):
            query = f"DESCRIBE SELECT * FROM read_parquet('{s3_path}')"
        elif path.endswith('.csv') or path.endswith('.csv.gz'):
            query = f"DESCRIBE SELECT * FROM read_csv_auto('{s3_path}')"
        elif path.endswith('.json') or path.endswith('.jsonl'):
            query = f"DESCRIBE SELECT * FROM read_json_auto('{s3_path}')"
        else:
            return {"success": False, "error": f"Unsupported format: {path}"}

        return self.execute_query(query)

    def preview_file(self, bucket: str, path: str, limit: int = 100) -> dict:
        """Preview first N rows of a file."""
        return self.query_s3_file(bucket, path, limit=limit)

    def close(self):
        """Close connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


# Singleton instance
duckdb_service = DuckDBService()
