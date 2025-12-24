import os
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
try:
    import psycopg2
except ImportError:
    psycopg2 = None

# Load .env if possible
if load_dotenv:
    load_dotenv()

if not psycopg2:
    print("psycopg2 not installed. Please install with: pip install psycopg2-binary")
    exit(1)

host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "")
db = os.getenv("POSTGRES_DB", "postgres")

print(f"Checking PostgreSQL connection to {host}:{port} db={db} user={user}")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=db,
        connect_timeout=5
    )
    print("PostgreSQL connection: SUCCESS")
    conn.close()
except Exception as e:
    print("PostgreSQL connection: FAILED")
    print(e)
