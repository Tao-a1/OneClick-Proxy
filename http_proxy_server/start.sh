#!/bin/bash
cd "$(dirname "$0")"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed."
    exit 1
fi

# 检查端口占用
if lsof -i :8083 > /dev/null; then
    echo "Warning: Port 8083 seems to be in use. Trying to start anyway..."
fi

echo "Starting HTTP Proxy Server..."
echo "Log file: proxy.log"
setsid /root/.nvm/versions/node/v25.3.0/bin/node proxy.js > proxy.log 2>&1 &
PID=$!
echo "Server started with PID: $PID"
echo $PID > proxy.pid
