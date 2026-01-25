#!/bin/bash
cd "$(dirname "$0")"

# 1. 尝试通过 PID 文件停止
if [ -f proxy.pid ]; then
    PID=$(cat proxy.pid)
    if ps -p $PID > /dev/null; then
        echo "Stopping Proxy Server (PID $PID)..."
        kill $PID
        rm proxy.pid
        echo "Stopped."
        exit 0
    else
        echo "Process $PID not found (stale pid file). Cleaning up."
        rm proxy.pid
    fi
fi

# 2. 兜底：通过端口停止
echo "Checking for any process on port 8083..."
PID=$(lsof -t -i:8083)
if [ ! -z "$PID" ]; then
    echo "Found process listening on 8083 (PID $PID). Killing it..."
    kill $PID
    echo "Stopped."
else
    echo "No process found on port 8083."
fi
