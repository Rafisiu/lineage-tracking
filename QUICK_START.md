# 🚀 Quick Start Guide

## ✅ Application is Running!

Your ClickHouse Migration & Query application is now live and publicly accessible.

### 🌐 Access URLs

- **Frontend (Web UI)**: http://172.19.0.2:5173/
- **Backend API**: http://0.0.0.0:3000
- **Health Check**: http://0.0.0.0:3000/health

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Frontend | ✅ Running | Full UI accessible on all network interfaces |
| Backend API | ✅ Running | Accepting requests on port 3000 |
| PostgreSQL | ✅ Connected | 140.0.219.7:5432 - Ready for use |
| ClickHouse | ❌ Not Connected | 140.0.219.7:8123 - Connection refused |

## 🎯 What You Can Do Now

### 1. Access the Web Interface
Open your browser to: **http://172.19.0.2:5173/**

You'll see three tabs:
- **Query**: Execute ClickHouse SQL queries (requires ClickHouse connection)
- **Migration**: Migrate data from PostgreSQL to ClickHouse
- **History**: View past migration records

### 2. Test PostgreSQL Schema Analysis

Even without ClickHouse, you can:

1. Go to the **Migration** tab
2. Enter a PostgreSQL table name in the "Source Configuration"
3. Leave connection fields empty to use the default PostgreSQL database
4. Click "Next: Analyze Schema"
5. View your table structure, columns, and types
6. Click "Next: Generate Mapping" to see auto-generated field mappings

### 3. Test the API Directly

```bash
# Health check
curl http://localhost:3000/health

# Analyze a PostgreSQL table (replace YOUR_TABLE with actual table name)
curl -X POST http://localhost:3000/api/migration/analyze-source \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "public",
    "table": "YOUR_TABLE"
  }'

# Get list of tables
curl http://localhost:3000/api/migration/tables?schema=public
```

## ⚙️ Managing the Application

### View Logs
The servers are running in background. To see logs:
```bash
# View current server output
# The servers are running as background process ID: 28ab21
```

### Restart Servers
If you need to restart after configuration changes:
```bash
# Stop current servers (Ctrl+C in the terminal running npm run dev)
# Or kill the background process

# Then restart
cd /home/coder/project/lineage-tracking
npm run dev
```

### Test Database Connections
```bash
cd /home/coder/project/lineage-tracking
bash test-connections.sh
```

## 🔧 Fixing ClickHouse Connection

The application is running but can't connect to ClickHouse. Here's how to fix it:

### Step 1: Verify ClickHouse Details
You need to confirm:
- Is ClickHouse running on 140.0.219.7?
- What port is it listening on?
- Can this container reach it?

### Step 2: Update Configuration
Edit the configuration file:
```bash
nano backend/.env
```

Update these lines:
```env
CLICKHOUSE_HOST=YOUR_CLICKHOUSE_HOST
CLICKHOUSE_PORT=YOUR_CLICKHOUSE_PORT
CLICKHOUSE_USER=YOUR_CLICKHOUSE_USER
CLICKHOUSE_PASSWORD=YOUR_CLICKHOUSE_PASSWORD
```

### Step 3: Restart Backend
```bash
touch backend/src/app.ts
```
The backend will automatically restart and try the new connection.

### Step 4: Verify
```bash
bash test-connections.sh
```

## 📖 Common ClickHouse Ports

- **8123** - HTTP interface (most common for web apps)
- **9000** - Native TCP protocol
- **8443** - HTTPS interface
- **9440** - Secure native protocol

## 🧪 Testing Features

### Working Right Now (without ClickHouse):
- ✅ PostgreSQL schema analysis
- ✅ Field mapping generation
- ✅ Type conversion (PostgreSQL → ClickHouse)
- ✅ DDL generation
- ✅ Frontend UI

### Will Work Once ClickHouse is Connected:
- ⏳ Execute ClickHouse queries
- ⏳ Create tables in ClickHouse
- ⏳ Migrate data PostgreSQL → ClickHouse
- ⏳ View migration history
- ⏳ Track migration lineage

## 📚 Documentation

- **README.md** - Complete documentation and setup guide
- **CONNECTION_STATUS.md** - Detailed connection diagnostics
- **DESIGN.md** - Architecture and design specifications
- **test-connections.sh** - Connection testing script

## 🆘 Troubleshooting

### Frontend not loading?
```bash
# Check if frontend is running
curl http://localhost:5173/

# If not, restart
cd frontend && npm run dev
```

### Backend not responding?
```bash
# Check backend health
curl http://localhost:3000/health

# If not, restart
cd backend && npm run dev
```

### Can't access from external network?
Both servers are configured to listen on all interfaces (0.0.0.0), so they should be accessible. Check:
- Firewall rules
- Security groups
- Network configuration

### Need to change ports?
Edit these files:
- Frontend port: `frontend/vite.config.ts` (server.port)
- Backend port: `backend/.env` (PORT)

## 🎉 Next Steps

1. **Fix ClickHouse connection** - Update backend/.env with correct details
2. **Create a test table** - Use the migration wizard to migrate a small table
3. **Run queries** - Try executing some ClickHouse queries
4. **Explore features** - Test all three tabs in the UI

## 📞 Support

If you have the correct ClickHouse connection details:
1. Update `backend/.env`
2. Restart: `touch backend/src/app.ts`
3. Test: `bash test-connections.sh`

Once ClickHouse is connected, you'll have a fully functional PostgreSQL → ClickHouse migration tool!

---

**Application Built With:**
- Backend: Fastify + TypeScript
- Frontend: Vue 3 + Element Plus
- Databases: PostgreSQL + ClickHouse
