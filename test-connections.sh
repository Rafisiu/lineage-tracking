#!/bin/bash

echo "==================================="
echo "Database Connection Test"
echo "==================================="
echo ""

# Load environment variables
if [ -f backend/.env ]; then
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

echo "Testing PostgreSQL Connection..."
echo "Host: $POSTGRES_HOST:$POSTGRES_PORT"
if timeout 3 bash -c "cat < /dev/null > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT" 2>/dev/null; then
    echo "✅ PostgreSQL port is OPEN"

    # Try to connect with psql if available
    if command -v psql &> /dev/null; then
        echo "Attempting database connection..."
        PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT version();" 2>&1 | head -3
    fi
else
    echo "❌ PostgreSQL port is CLOSED or unreachable"
fi

echo ""
echo "-----------------------------------"
echo "Testing ClickHouse Connection..."
echo "Host: $CLICKHOUSE_HOST:$CLICKHOUSE_PORT"

# Test common ClickHouse ports
for port in 8123 9000 9440 8443 8546; do
    if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$CLICKHOUSE_HOST/$port" 2>/dev/null; then
        echo "✅ Port $port is OPEN"

        # If port 8123 is open, try HTTP request
        if [ "$port" = "8123" ]; then
            echo "Testing HTTP interface..."
            curl -s --max-time 3 "http://$CLICKHOUSE_HOST:$port/ping" && echo "" && echo "HTTP interface is working!"
        fi
    else
        echo "❌ Port $port is CLOSED"
    fi
done

echo ""
echo "-----------------------------------"
echo "Configured ClickHouse Port: $CLICKHOUSE_PORT"
if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$CLICKHOUSE_HOST/$CLICKHOUSE_PORT" 2>/dev/null; then
    echo "✅ Configured port is accessible"

    # Try HTTP ping
    echo "Testing ClickHouse HTTP ping..."
    response=$(curl -s --max-time 3 "http://$CLICKHOUSE_HOST:$CLICKHOUSE_PORT/ping" 2>&1)
    if [ $? -eq 0 ]; then
        echo "✅ ClickHouse HTTP ping successful: $response"
    else
        echo "❌ HTTP ping failed: $response"
    fi
else
    echo "❌ Configured port is NOT accessible"
    echo ""
    echo "Possible issues:"
    echo "1. ClickHouse is not running on $CLICKHOUSE_HOST"
    echo "2. Firewall is blocking the connection"
    echo "3. Wrong port configured (current: $CLICKHOUSE_PORT)"
    echo "4. ClickHouse is configured to listen on localhost only"
    echo ""
    echo "Common ClickHouse ports:"
    echo "  - 8123  (HTTP interface)"
    echo "  - 9000  (Native protocol)"
    echo "  - 8443  (HTTPS interface)"
fi

echo ""
echo "==================================="
echo "Application Status"
echo "==================================="

# Check if backend is running
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running on http://localhost:3000"
    echo "✅ Frontend should be accessible at http://172.19.0.2:5173/"
else
    echo "❌ Backend API is not responding"
fi

echo ""
echo "==================================="
