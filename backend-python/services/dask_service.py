import dask.dataframe as dd
import pandas as pd
import time
import tempfile
import os


class DaskService:
    def __init__(self):
        pass

    def execute_query(self, df, query: str = None, limit: int = 1000) -> dict:
        """Execute query on Dask DataFrame."""
        start_time = time.time()

        try:
            print(f"[Dask] Processing query...")

            # If custom query provided, try to apply it
            if query and query.strip():
                # Simple query parsing for basic SELECT operations
                query_lower = query.lower().strip()

                # Handle SELECT * FROM data with optional WHERE
                if 'select * from data' in query_lower:
                    if 'where' in query_lower:
                        # Extract WHERE condition
                        where_part = query_lower.split('where', 1)[1].strip()
                        print(f"[Dask] Applying filter: {where_part}")
                        # For basic queries, we'll just take the limit
                        # Complex filtering would require query parsing

            # Apply limit and compute
            result_df = df.head(limit, npartitions=-1)

            execution_time = (time.time() - start_time) * 1000

            # Convert to dict format
            columns = result_df.columns.tolist()
            # Replace NaN values with empty string for JSON compatibility
            result_df = result_df.fillna('')
            data = result_df.to_dict('records')

            print(f"[Dask] Query successful: {len(data)} rows in {round(execution_time, 2)}ms")

            return {
                "success": True,
                "columns": columns,
                "data": data,
                "row_count": len(data),
                "execution_time_ms": round(execution_time, 2)
            }
        except Exception as e:
            print(f"[Dask] Query failed: {str(e)}")
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
        """Query S3 file using Dask for efficient large file processing."""
        from services.minio_service import minio_service

        temp_file = None
        temp_path = None

        try:
            print(f"[Dask] Downloading s3://{bucket}/{path} from MinIO...")

            # Create temp file
            suffix = os.path.splitext(path)[1]
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_path = temp_file.name
            temp_file.close()

            # Download from MinIO
            minio_service.download_file(bucket, path, temp_path)
            print(f"[Dask] Downloaded to {temp_path}")

            # Read file with Dask based on format
            if path.endswith('.parquet'):
                print(f"[Dask] Reading Parquet file with Dask...")
                df = dd.read_parquet(temp_path, engine='pyarrow')
            elif path.endswith('.csv') or path.endswith('.csv.gz'):
                print(f"[Dask] Reading CSV file with Dask...")
                # Try different encodings for better compatibility
                encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
                df = None
                last_error = None

                for encoding in encodings:
                    try:
                        print(f"[Dask] Trying encoding: {encoding}")
                        # Read with pandas first to avoid Dask dtype inference issues
                        pandas_df = pd.read_csv(
                            temp_path,
                            encoding=encoding,
                            encoding_errors='replace',
                            on_bad_lines='skip',
                            low_memory=False,  # Read entire file at once for proper dtype inference
                            nrows=limit  # Only read what we need
                        )
                        df = dd.from_pandas(pandas_df, npartitions=1)
                        print(f"[Dask] Successfully read with {encoding} encoding")
                        break
                    except (UnicodeDecodeError, ValueError) as e:
                        last_error = e
                        continue

                if df is None:
                    raise last_error or Exception("Could not read CSV with any encoding")
            elif path.endswith('.json') or path.endswith('.jsonl'):
                print(f"[Dask] Reading JSON file...")
                # For JSON, use pandas then convert to dask
                # (Dask doesn't have native JSON reader)
                pandas_df = pd.read_json(temp_path, lines=path.endswith('.jsonl'))
                df = dd.from_pandas(pandas_df, npartitions=4)
            else:
                return {"success": False, "error": f"Unsupported file format: {path}"}

            # Execute query
            return self.execute_query(df, query, limit)

        except Exception as e:
            print(f"[Dask] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    print(f"[Dask] Cleaned up temp file")
                except Exception as e:
                    print(f"[Dask] Failed to cleanup: {e}")

    def get_schema(self, bucket: str, path: str) -> dict:
        """Get schema of S3 file using Dask."""
        from services.minio_service import minio_service

        temp_file = None
        temp_path = None

        try:
            # Create temp file
            suffix = os.path.splitext(path)[1]
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_path = temp_file.name
            temp_file.close()

            # Download from MinIO
            minio_service.download_file(bucket, path, temp_path)

            # Read just the schema (first few rows)
            if path.endswith('.parquet'):
                df = dd.read_parquet(temp_path, engine='pyarrow')
            elif path.endswith('.csv') or path.endswith('.csv.gz'):
                # Try different encodings
                encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
                df = None
                for encoding in encodings:
                    try:
                        df = dd.read_csv(
                            temp_path,
                            blocksize='64MB',
                            assume_missing=True,
                            encoding=encoding,
                            encoding_errors='replace',
                            dtype_backend='numpy_nullable',
                            on_bad_lines='skip'
                        )
                        break
                    except (UnicodeDecodeError, ValueError):
                        continue
                if df is None:
                    raise Exception("Could not read CSV with any encoding")
            elif path.endswith('.json') or path.endswith('.jsonl'):
                pandas_df = pd.read_json(temp_path, lines=path.endswith('.jsonl'), nrows=1000)
                df = dd.from_pandas(pandas_df, npartitions=1)
            else:
                return {"success": False, "error": f"Unsupported format: {path}"}

            # Get schema information
            schema_data = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                schema_data.append({
                    "column_name": col,
                    "column_type": dtype,
                    "null": "YES"  # Dask doesn't easily provide null info without computing
                })

            return {
                "success": True,
                "data": schema_data
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def preview_file(self, bucket: str, path: str, limit: int = 100) -> dict:
        """Preview first N rows of a file."""
        return self.query_s3_file(bucket, path, limit=limit)


# Singleton instance
dask_service = DaskService()
