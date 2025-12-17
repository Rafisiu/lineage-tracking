# ClickHouse Migration & Query Application

A full-stack web application for executing ClickHouse queries and migrating data from PostgreSQL to ClickHouse with automatic schema mapping, lineage tracking, and S3/MinIO data integration capabilities.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites & Installation](#prerequisites--installation)
- [Running the Application](#running-the-application)
- [Architecture & Design](#architecture--design)
- [Database Schema](#database-schema)
- [Type Mapping](#type-mapping)
- [API Documentation](#api-documentation)
- [Usage Guide](#usage-guide)
- [S3 Integration](#s3-integration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## Features

### Query Execution
- Execute ClickHouse SQL queries through a web interface
- View results in a formatted table
- See execution time and row count
- Syntax highlighting for SQL queries
- Query history tracking

### Data Migration
- **Automated Schema Analysis**: Analyze PostgreSQL table structure
- **Intelligent Type Mapping**: Automatic PostgreSQL to ClickHouse type conversion
- **Field Mapping Editor**: Customize field names, types, and skip unwanted fields
- **Migration Tracking**: Complete history of all migrations with detailed metadata
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Progress Monitoring**: Real-time migration progress tracking
- **Error Handling**: Comprehensive error logging and recovery

### Migration History & Lineage
- View all past migrations with status, duration, and record counts
- Detailed migration information including field mappings
- Filter by migration status (pending, running, completed, failed)
- Searchable and sortable migration log
- Complete lineage tracking of data transformations

### S3 Data Integration
- Query data directly from S3/MinIO buckets
- Support for multiple file formats (Parquet, CSV, JSON)
- File browser for S3/MinIO
- Direct SQL queries on S3 data using ClickHouse or DuckDB
- Distributed processing with Dask for large datasets

---

## Technology Stack

### Backend
- **Runtime**: Node.js with TypeScript
- **Framework**: Fastify (high-performance async web framework)
- **Database Clients**:
  - \`@clickhouse/client\` - Official ClickHouse client
  - \`pg\` - PostgreSQL client
- **Validation**: Zod for request validation
- **Logging**: Pino with pretty printing

### Frontend
- **Framework**: Vue 3 with Composition API
- **Build Tool**: Vite
- **UI Library**: Element Plus
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Router**: Vue Router 4

### Optional: S3 Explorer Extension
- **Python Backend**: FastAPI with MinIO client
- **Query Engines**: DuckDB for SQL, Dask for distributed processing
- **Storage**: MinIO (S3-compatible)

---

## Project Structure

\`\`\`
lineage-tracking/
├── backend/                 # Node.js Backend API
│   ├── src/
│   │   ├── config/         # Database and server configuration
│   │   ├── controllers/    # Request handlers
│   │   │   ├── query.controller.ts       # Query execution
│   │   │   └── migration.controller.ts   # Migration operations
│   │   ├── models/         # TypeScript interfaces
│   │   │   ├── schema.model.ts           # Schema definitions
│   │   │   └── migration.model.ts        # Migration types
│   │   ├── routes/         # API routes
│   │   │   ├── query.routes.ts
│   │   │   └── migration.routes.ts
│   │   ├── services/       # Business logic
│   │   │   ├── clickhouse.service.ts     # ClickHouse operations
│   │   │   ├── postgres.service.ts       # PostgreSQL operations
│   │   │   ├── migration.service.ts      # Migration logic
│   │   │   ├── mapping.service.ts        # Type mapping
│   │   │   └── history.service.ts        # History tracking
│   │   ├── utils/          # Utilities
│   │   │   ├── type-mapper.ts            # Type conversions
│   │   │   └── validator.ts              # Input validation
│   │   └── app.ts          # Application entry point
│   ├── .env                # Environment variables
│   ├── package.json
│   └── tsconfig.json
│
├── frontend/               # Vue.js Frontend App
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── router/        # Vue Router configuration
│   │   ├── stores/        # Pinia stores
│   │   │   ├── query.store.ts          # Query state
│   │   │   └── migration.store.ts      # Migration state
│   │   ├── views/         # Page components
│   │   │   ├── QueryView.vue           # SQL query interface
│   │   │   ├── MigrationView.vue       # Migration wizard
│   │   │   └── HistoryView.vue         # Migration history
│   │   ├── components/    # Reusable components
│   │   │   ├── query/
│   │   │   │   ├── SqlEditor.vue       # SQL editor
│   │   │   │   ├── ResultTable.vue     # Results display
│   │   │   │   └── QueryHistory.vue    # Query history
│   │   │   ├── migration/
│   │   │   │   ├── ConnectionForm.vue  # DB connection
│   │   │   │   ├── SchemaAnalyzer.vue  # Schema display
│   │   │   │   ├── MappingEditor.vue   # Field mapping
│   │   │   │   └── MigrationProgress.vue # Progress indicator
│   │   │   └── shared/
│   │   │       ├── DataTable.vue       # Table component
│   │   │       └── StatusBadge.vue     # Status indicator
│   │   ├── composables/   # Composition functions
│   │   │   ├── useQuery.ts             # Query logic
│   │   │   ├── useMigration.ts         # Migration logic
│   │   │   └── useHistory.ts           # History logic
│   │   ├── App.vue        # Root component
│   │   └── main.ts        # Application entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── docker-compose.yml      # Docker services configuration
├── DOCUMENTATION.md        # This comprehensive documentation
├── package.json           # Root package.json for workspace
└── README.md
\`\`\`

---

## Prerequisites & Installation

### Prerequisites

- **Node.js 18+** and npm
- **PostgreSQL database** (for migration source)
- **ClickHouse database** (for migration destination and queries)
- **Docker & Docker Compose** (optional, for containerized deployment)

### Installation

#### 1. Install Dependencies

\`\`\`bash
# Install root dependencies
npm install

# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install

# Return to root
cd ..
\`\`\`

#### 2. Configure Environment Variables

Create or edit \`backend/.env\` with your database credentials:

\`\`\`env
# Server Configuration
PORT=3000
NODE_ENV=development

# PostgreSQL Configuration
POSTGRES_HOST=140.0.219.7
POSTGRES_PORT=5432
POSTGRES_USER=root
POSTGRES_PASSWORD=ANSKk08aPEDbFjDO
POSTGRES_DB=postgres

# ClickHouse Configuration
CLICKHOUSE_HOST=140.0.219.7
CLICKHOUSE_PORT=8546
CLICKHOUSE_USER=tdi
CLICKHOUSE_PASSWORD=ANSKk08aPEDbFjDO
CLICKHOUSE_DATABASE=default

# Optional: S3/MinIO Configuration
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# S3_ENDPOINT=https://s3.amazonaws.com
\`\`\`

---

## Running the Application

### Development Mode

#### Run Both Services Concurrently

\`\`\`bash
# From root directory
npm run dev
\`\`\`

#### Run Services Separately

\`\`\`bash
# Terminal 1 - Backend
cd backend
npm run dev

# Terminal 2 - Frontend
cd frontend
npm run dev
\`\`\`

**Access URLs:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000

### Production Build

\`\`\`bash
# Build backend
cd backend
npm run build
npm start

# Build frontend
cd frontend
npm run build
npm run preview
\`\`\`

### Docker Compose Deployment

\`\`\`bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
\`\`\`

---

## Architecture & Design

### High-Level Architecture

\`\`\`
┌─────────────────┐
│   Vue.js App    │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Fastify API    │
│   (Backend)     │
└────┬─────┬──────┘
     │     │
     ▼     ▼
┌─────────┐  ┌──────────┐
│PostgreSQL│  │ClickHouse│
└─────────┘  └──────────┘
\`\`\`

### Migration Workflow

1. **Connect & Analyze**
   - User provides PostgreSQL connection details
   - Backend queries \`information_schema\` to get table structure
   - Return column definitions, constraints, row counts

2. **Generate Mapping**
   - Apply type mapping rules (PostgreSQL → ClickHouse)
   - Suggest ClickHouse table structure
   - Detect potential issues (unsupported types)

3. **User Review**
   - Display suggested mappings in UI
   - Allow modifications:
     - Rename fields
     - Change types
     - Add transformations (CAST, toString)
     - Skip fields

4. **Table Creation** (if enabled)
   - Generate CREATE TABLE DDL
   - Execute on ClickHouse
   - Handle errors gracefully

5. **Data Migration**
   - Fetch data in batches from PostgreSQL
   - Transform according to mappings
   - Insert into ClickHouse using \`INSERT FORMAT\`
   - Update progress in real-time

6. **History Recording**
   - Insert into \`migration_history\` table
   - Include all metadata, mappings, results

7. **Completion**
   - Display summary statistics
   - Show migration history entry
   - Offer to query new table

### Frontend Views

#### 1. Query View
- SQL editor with syntax highlighting
- Execute button
- Results table with pagination
- Export results (CSV, JSON)
- Query history sidebar

#### 2. Migration View (Wizard Steps)
1. **Source Configuration**: Connect to PostgreSQL, select schema/table
2. **Schema Analysis**: Display source table structure, row count, size
3. **Mapping Configuration**:
   - Show suggested mappings
   - Allow user to modify field names, types, transformations
   - Preview DDL
4. **Migration Options**: Batch size, create table, description
5. **Execution**: Start migration, show progress
6. **Summary**: Results, errors, history entry link

#### 3. History View
- Table of all migrations
- Filters: date range, status, source, destination
- Search by description
- Click to view details:
  - Field mappings used
  - Migration metadata
  - Error logs if failed
  - Re-run option

---

## Database Schema

### Migration History Table

The application automatically creates a \`migration_history\` table in ClickHouse:

\`\`\`sql
CREATE TABLE IF NOT EXISTS migration_history (
    id UUID DEFAULT generateUUIDv4(),
    source String,                    -- Source database identifier
    destination String,                -- Destination table in ClickHouse
    source_table String,               -- Source table name
    migration_time DateTime DEFAULT now(),
    deskripsi String,                  -- Description/notes
    tabel_fields Array(String),        -- List of fields migrated
    field_mappings String,             -- JSON string of field mappings
    status Enum8('pending' = 1, 'running' = 2, 'completed' = 3, 'failed' = 4),
    records_migrated UInt64,           -- Number of records migrated
    error_message Nullable(String),    -- Error details if failed
    duration_seconds UInt32,           -- Migration duration
    created_by String,                 -- User who initiated migration
    metadata String                    -- Additional metadata as JSON
) ENGINE = MergeTree()
ORDER BY (migration_time, id)
PARTITION BY toYYYYMM(migration_time);
\`\`\`

---

## Type Mapping

### PostgreSQL to ClickHouse Type Mapping

The application automatically maps PostgreSQL types to ClickHouse types:

| PostgreSQL Type | ClickHouse Type |
|----------------|-----------------|
| smallint, int2 | Int16 |
| integer, int, int4 | Int32 |
| bigint, int8 | Int64 |
| real, float4 | Float32 |
| double precision, float8 | Float64 |
| numeric, decimal | Decimal128(38) |
| varchar, text | String |
| char | FixedString |
| date | Date |
| timestamp | DateTime |
| timestamptz | DateTime64(3) |
| boolean | UInt8 |
| json, jsonb | String |
| uuid | UUID |
| ARRAY | Array |

### Nullable Handling
- PostgreSQL nullable fields → ClickHouse \`Nullable(Type)\`
- Primary keys remain non-nullable

---

## API Documentation

### Query API

#### Execute Query
\`\`\`http
POST /api/query/execute
Content-Type: application/json

{
  "query": "SELECT * FROM system.tables LIMIT 10",
  "format": "JSON"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "data": [...],
  "rows": 10,
  "execution_time_ms": 45,
  "metadata": {
    "columns": [...],
    "types": [...]
  }
}
\`\`\`

#### Health Check
\`\`\`http
GET /api/query/health
\`\`\`

#### Get Query History
\`\`\`http
GET /api/query/history?limit=50
\`\`\`

### Migration API

#### Analyze Source Table
\`\`\`http
POST /api/migration/analyze-source
Content-Type: application/json

{
  "schema": "public",
  "table": "users",
  "connection": {  // Optional - uses default if not provided
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres",
    "password": "password"
  }
}
\`\`\`

**Response:**
\`\`\`json
{
  "table": "users",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "nullable": false,
      "primary_key": true
    },
    {
      "name": "email",
      "type": "varchar",
      "nullable": false
    }
  ],
  "row_count": 10000,
  "estimated_size_mb": 5.2
}
\`\`\`

#### Suggest Field Mapping
\`\`\`http
POST /api/migration/suggest-mapping
Content-Type: application/json

{
  "source_schema": { ... },  // From analyze-source response
  "destination_table": "users_clickhouse"
}
\`\`\`

**Response:**
\`\`\`json
{
  "suggested_ddl": "CREATE TABLE users_clickhouse (...)",
  "mappings": [
    {
      "source_field": "id",
      "source_type": "integer",
      "destination_field": "id",
      "destination_type": "UInt32",
      "transformation": null
    }
  ],
  "warnings": []
}
\`\`\`

#### Execute Migration
\`\`\`http
POST /api/migration/execute
Content-Type: application/json

{
  "source_schema": "public",
  "source_table": "users",
  "destination_table": "users_clickhouse",
  "mappings": [ ... ],
  "create_table": true,
  "batch_size": 10000,
  "description": "Initial user data migration"
}
\`\`\`

**Response:**
\`\`\`json
{
  "migration_id": "uuid",
  "status": "running"
}
\`\`\`

#### Get Migration Status
\`\`\`http
GET /api/migration/status/:migration_id
\`\`\`

**Response:**
\`\`\`json
{
  "id": "uuid",
  "status": "running",
  "progress": {
    "total_records": 100000,
    "processed_records": 45000,
    "percentage": 45
  },
  "started_at": "2024-01-01T10:00:00Z",
  "estimated_completion": "2024-01-01T10:05:00Z"
}
\`\`\`

#### Get Migration History
\`\`\`http
GET /api/migration/history?limit=20&offset=0&status=completed
\`\`\`

**Response:**
\`\`\`json
{
  "migrations": [
    {
      "id": "uuid",
      "source": "postgres://localhost/mydb",
      "destination": "users_clickhouse",
      "source_table": "users",
      "migration_time": "2024-01-01T10:00:00Z",
      "status": "completed",
      "records_migrated": 100000,
      "duration_seconds": 120
    }
  ],
  "total": 50
}
\`\`\`

---

## Usage Guide

### 1. Execute ClickHouse Queries

1. Navigate to the **Query** tab
2. Enter your SQL query in the editor
3. Click **Execute Query**
4. View results in the table below

**Example queries:**
\`\`\`sql
-- View all tables
SELECT * FROM system.tables LIMIT 10;

-- Check database size
SELECT database, sum(bytes) as size
FROM system.parts
GROUP BY database;

-- Query specific table
SELECT * FROM your_table
WHERE date >= '2024-01-01'
LIMIT 100;
\`\`\`

### 2. Migrate Data from PostgreSQL

1. Navigate to the **Migration** tab

2. **Step 1: Source Configuration**
   - Enter schema name (default: \`public\`)
   - Enter table name
   - Optionally provide custom PostgreSQL connection details
   - Click **Next: Analyze Schema**

3. **Step 2: Schema Analysis**
   - Review the source table structure
   - Check row count and estimated size
   - Click **Next: Generate Mapping**

4. **Step 3: Mapping Configuration**
   - Enter destination table name
   - Review and customize field mappings
   - Modify field names or types as needed
   - Check fields to skip if not needed
   - Review generated DDL
   - Configure batch size (default: 10000)
   - Add migration description
   - Click **Start Migration**

5. **Step 4: Execution**
   - Monitor migration progress
   - View real-time status updates
   - Wait for completion

6. **Step 5: Completion**
   - View completion status and statistics
   - Check for any errors
   - Access the new table in ClickHouse

### 3. View Migration History

1. Navigate to the **History** tab
2. View all past migrations
3. Use filters to find specific migrations:
   - Filter by status (completed, running, failed)
   - Search by description
   - Sort by date or duration
4. Click **Details** to see:
   - Complete field mappings
   - Migration metadata
   - Error logs (if failed)
   - Performance statistics

---

## S3 Integration

### Overview

The application can be extended to query data stored in S3/MinIO buckets. There are multiple approaches:

### 1. ClickHouse S3 Functions (Recommended)

Since the application already uses ClickHouse, this is the easiest integration option.

#### Direct S3 Query

\`\`\`sql
-- Query CSV file from S3
SELECT *
FROM s3(
    'https://bucket-name.s3.amazonaws.com/path/to/file.csv',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'CSV',
    'column1 String, column2 Int32, column3 Float64'
)
LIMIT 100;

-- Query Parquet file
SELECT *
FROM s3(
    'https://bucket-name.s3.region.amazonaws.com/data/*.parquet',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'Parquet'
);

-- Query with glob patterns (multiple files)
SELECT *
FROM s3(
    'https://bucket-name.s3.amazonaws.com/logs/2024/*/data_*.csv.gz',
    'key',
    'secret',
    'CSVWithNames',
    'auto'
)
WHERE date >= '2024-01-01';
\`\`\`

#### Create S3-backed Table

\`\`\`sql
-- Create a table engine that reads from S3
CREATE TABLE s3_data (
    id Int32,
    name String,
    value Float64,
    created_at DateTime
) ENGINE = S3(
    'https://bucket-name.s3.amazonaws.com/data/',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'Parquet'
);

-- Query like a regular table
SELECT * FROM s3_data WHERE created_at > '2024-01-01';
\`\`\`

#### S3Queue for Streaming

\`\`\`sql
-- Continuously ingest new files from S3
CREATE TABLE s3_queue (
    id Int32,
    data String
) ENGINE = S3Queue(
    'https://bucket.s3.amazonaws.com/queue/',
    'key',
    'secret',
    'JSONEachRow'
)
SETTINGS
    mode = 'ordered',
    s3queue_loading_retries = 3;
\`\`\`

### 2. Integration with Current Application

To add S3 query support to the existing backend:

1. **Add S3 credentials to \`.env\`:**
\`\`\`env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_ENDPOINT=https://s3.amazonaws.com
S3_REGION=us-east-1
\`\`\`

2. **Create S3 query endpoint:**
\`\`\`typescript
// Add to query.controller.ts
@router.post("/api/query/s3")
async function queryS3(request, reply) {
  const { bucket, path, format = 'Parquet' } = request.body;

  const query = \`
    SELECT * FROM s3(
      'https://\${bucket}.s3.amazonaws.com/\${path}',
      '\${process.env.AWS_ACCESS_KEY_ID}',
      '\${process.env.AWS_SECRET_ACCESS_KEY}',
      '\${format}'
    ) LIMIT 1000
  \`;

  return clickhouseService.executeQuery(query);
}
\`\`\`

### 3. Alternative: S3 Data Explorer System

For more advanced S3 operations, you can set up a separate Python-based system using MinIO, DuckDB, and Dask. See the detailed architecture in the S3_DATA_EXPLORER.md file for:

- MinIO file browser
- DuckDB SQL queries on S3 data
- Dask distributed processing
- Complete API endpoints for S3 operations

### S3 Integration Comparison

| Tool | Best For | Pricing | Setup Complexity |
|------|----------|---------|------------------|
| **ClickHouse S3** | Already using ClickHouse | Free (self-hosted) | Low |
| **Athena** | Serverless, occasional queries | $5/TB scanned | Low |
| **DuckDB** | Local analysis, small-medium data | Free | Very Low |
| **Trino** | Large-scale analytics | Free (self-hosted) | Medium |
| **Spark SQL** | ETL, ML pipelines | Free (self-hosted) | High |

---

## Deployment

### Docker Compose Deployment

The application includes a \`docker-compose.yml\` for easy deployment:

\`\`\`yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: lineage-backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PORT=3000
    env_file:
      - ./backend/.env
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: lineage-frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    restart: unless-stopped

  # Optional: nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: lineage-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
\`\`\`

### Production Deployment Commands

\`\`\`bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# View service status
docker-compose ps
\`\`\`

### Deployment Architecture

\`\`\`
┌─────────────────┐
│  Nginx/Caddy    │  (Reverse proxy, SSL)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Vue App│ │ Fastify │  (Docker containers)
│(Static)│ │   API   │
└────────┘ └────┬────┘
                │
          ┌─────┴─────┐
          │           │
     ┌────▼───┐  ┌────▼────┐
     │Postgres│  │ClickHouse│
     └────────┘  └─────────┘
\`\`\`

### Security Considerations

1. **Connection Credentials**
   - Never store credentials in frontend
   - Use environment variables
   - Encrypt at rest if persisting
   - Rotate credentials regularly

2. **SQL Injection Prevention**
   - Use parameterized queries only
   - Validate all user inputs with Zod
   - Whitelist allowed query patterns

3. **Access Control**
   - Implement user authentication (JWT)
   - Role-based access control (RBAC)
   - Audit log for all operations

4. **Rate Limiting**
   - Limit query execution frequency
   - Prevent resource exhaustion
   - Set timeout limits

### Performance Optimizations

1. **Query Execution**
   - Timeout limits (default: 60s)
   - Result size limits
   - Streaming for large results
   - Query result caching

2. **Migration**
   - Configurable batch sizes
   - Parallel batch processing
   - Resume on failure capability
   - Connection pooling

3. **Frontend**
   - Virtual scrolling for large result sets
   - Debounced search/filter
   - Lazy loading for history
   - Code splitting with Vite

---

## Troubleshooting

### Backend Issues

#### Backend won't start
- Check that port 3000 is not already in use: \`lsof -i :3000\`
- Verify database connection details in \`.env\`
- Ensure ClickHouse and PostgreSQL are accessible
- Check logs: \`npm run dev\` (in backend directory)

#### Cannot connect to databases
- Verify IP addresses and ports in \`.env\`
- Check firewall rules
- Test connectivity using database clients:
  \`\`\`bash
  # Test PostgreSQL
  psql -h 140.0.219.7 -p 5432 -U root -d postgres

  # Test ClickHouse
  curl http://140.0.219.7:8546
  \`\`\`

### Migration Issues

#### Migration fails immediately
- Check source table exists and is accessible
- Verify destination table name is valid ClickHouse identifier
- Review field mappings for type compatibility
- Check ClickHouse user has CREATE TABLE permissions

#### Migration stalls
- Check network connectivity
- Verify batch size isn't too large (try reducing to 5000)
- Check available disk space on ClickHouse server
- Review ClickHouse logs for errors

#### Type conversion errors
- Review the type mapping table
- Some PostgreSQL types may need manual mapping
- Use transformations for complex conversions
- Check for NULL values in non-nullable fields

### Frontend Issues

#### Frontend build errors
- Delete \`node_modules\` and reinstall: \`npm install\`
- Clear Vite cache: \`rm -rf frontend/.vite\`
- Check Node.js version: \`node -v\` (should be 18+)
- Clear browser cache

#### Cannot reach backend API
- Verify backend is running on port 3000
- Check CORS configuration in backend
- Verify API URL in frontend configuration
- Check browser console for errors

### Docker Issues

#### Container fails to start
\`\`\`bash
# View container logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose build --no-cache

# Remove old containers and volumes
docker-compose down -v
docker-compose up -d
\`\`\`

#### Out of memory errors
- Increase Docker memory limit
- Reduce batch size in migrations
- Check for memory leaks in logs

---

## Future Enhancements

### Planned Features

1. **Scheduled Migrations**
   - Cron-based recurring migrations
   - Automated sync schedules
   - Email notifications on completion

2. **Incremental Sync**
   - Sync only new/changed records
   - Change data capture (CDC)
   - Timestamp-based incremental updates

3. **Multi-Source Support**
   - MySQL support
   - MS SQL Server support
   - MongoDB support
   - CSV/Excel file imports

4. **Data Validation**
   - Compare source vs. destination row counts
   - Data integrity checks
   - Validation rules configuration

5. **Transformation Rules**
   - Custom JavaScript transformations
   - SQL-based transformations
   - Reusable transformation templates

6. **Query Templates**
   - Saved queries with parameters
   - Query snippets library
   - Share queries between users

7. **Visualization**
   - Basic charting for query results
   - Migration statistics dashboard
   - Performance metrics visualization

8. **Collaboration**
   - User authentication and authorization
   - Share migrations and queries
   - Team workspaces

9. **Version Control**
   - Track schema changes over time
   - Migration version history
   - Rollback capabilities

10. **Monitoring & Alerting**
    - Real-time performance dashboards
    - Alert on migration failures
    - Resource usage monitoring
    - Integration with Prometheus/Grafana

### S3 Enhancements

11. **Advanced S3 Features**
    - File browser UI for S3/MinIO
    - Direct upload to S3
    - S3 to ClickHouse migration
    - Scheduled S3 data imports

12. **Query Optimization**
    - Query result caching
    - Materialized views
    - Partition optimization recommendations

---

## Contributing

This project was built based on requirements and design specifications. Contributions are welcome!

### Development Guidelines

1. Follow TypeScript best practices
2. Use ESLint and Prettier for code formatting
3. Write tests for new features
4. Update documentation for API changes
5. Follow the existing code structure

### Running Tests

\`\`\`bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
\`\`\`

---

## License

MIT License

---

## Support

For issues, questions, or contributions, please refer to the project repository.

**Documentation Version:** 1.0.0  
**Last Updated:** 2025-01-25
