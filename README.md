# ClickHouse Migration & Query Application

A full-stack web application for executing ClickHouse queries and migrating data from PostgreSQL to ClickHouse with automatic schema mapping, lineage tracking, and S3/MinIO data integration.

## Quick Overview

This application provides:
- **Query Execution**: Execute ClickHouse SQL queries through a web interface
- **Data Migration**: Automated PostgreSQL to ClickHouse migration with intelligent type mapping
- **Lineage Tracking**: Complete migration history with detailed metadata
- **S3 Integration**: Query data directly from S3/MinIO buckets

## Technology Stack

- **Backend**: Node.js, TypeScript, Fastify
- **Frontend**: Vue 3, Vite, Element Plus
- **Databases**: PostgreSQL (source), ClickHouse (destination)

## Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL database
- ClickHouse database
- Docker & Docker Compose (optional)

### Installation

```bash
# Install dependencies
npm install
cd backend && npm install
cd ../frontend && npm install

# Configure environment variables
# Edit backend/.env with your database credentials

# Run the application
npm run dev
```

**Access URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:3000

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Documentation

**📚 For complete documentation, see [DOCUMENTATION.md](./DOCUMENTATION.md)**

The comprehensive documentation includes:
- Detailed installation instructions
- Complete API documentation
- Architecture and design details
- Migration workflow guide
- S3 integration examples
- Troubleshooting guide
- Future enhancements

**🚀 For quick setup guide, see [QUICK_START.md](./QUICK_START.md)**

## Project Structure

```
lineage-tracking/
├── backend/          # Node.js Fastify API
├── frontend/         # Vue 3 application
├── docker-compose.yml
├── DOCUMENTATION.md  # Complete documentation
├── QUICK_START.md    # Quick setup guide
└── README.md        # This file
```

## Basic Usage

### 1. Execute Queries
Navigate to the Query tab and execute ClickHouse SQL queries.

### 2. Migrate Data
Use the Migration wizard to migrate PostgreSQL tables to ClickHouse:
1. Configure source connection
2. Analyze schema
3. Review and customize field mappings
4. Execute migration

### 3. View History
Check the History tab for all past migrations with detailed information.

## Key Features

### Automated Type Mapping
PostgreSQL types are automatically mapped to ClickHouse types:
- `integer` → `Int32`
- `varchar/text` → `String`
- `timestamp` → `DateTime`
- `boolean` → `UInt8`

### Migration Tracking
All migrations are tracked in a `migration_history` table with:
- Source and destination information
- Field mappings used
- Records migrated
- Duration and status
- Error logs (if failed)

### S3 Integration
Query data from S3/MinIO using ClickHouse S3 functions or set up a Python-based explorer with DuckDB and Dask.

## API Endpoints

### Query API
- `POST /api/query/execute` - Execute ClickHouse query
- `GET /api/query/health` - Health check
- `GET /api/query/history` - Query history

### Migration API
- `POST /api/migration/analyze-source` - Analyze PostgreSQL table
- `POST /api/migration/suggest-mapping` - Get suggested mappings
- `POST /api/migration/execute` - Execute migration
- `GET /api/migration/status/:id` - Get migration status
- `GET /api/migration/history` - Get migration history

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check port 3000 is available
- Verify database credentials in `.env`
- Ensure databases are accessible

**Migration fails:**
- Verify source table exists
- Check ClickHouse permissions
- Review field mappings for compatibility

**Frontend errors:**
- Clear `node_modules` and reinstall
- Clear Vite cache: `rm -rf frontend/.vite`
- Check Node.js version (18+ required)

For detailed troubleshooting, see [DOCUMENTATION.md](./DOCUMENTATION.md#troubleshooting).

## Development

```bash
# Backend development
cd backend
npm run dev

# Frontend development
cd frontend
npm run dev

# Build for production
npm run build
```

## Contributing

Contributions are welcome! Please follow the existing code structure and update documentation for any changes.

## License

MIT

---

**For complete documentation, API reference, architecture details, and more, see [DOCUMENTATION.md](./DOCUMENTATION.md)**
