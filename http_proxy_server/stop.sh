#!/bin/bash
cd "$(dirname "$0")"

if [ -f proxy.pid ]; then
    PID=$(cat proxy.pid)
    if ps -p $PID > /dev/null; then
        echo "Stopping Proxy Server (PID $PID)..."
        kill $PID
        rm proxy.pid
        echo "Stopped."
    else
        echo "Process $PID not found. Cleaning up pid file."
        rm proxy.pid
    fi
else
    echo "No proxy.pid file found. Is the server running?"
    # 尝试根据端口查找
    PID=$(lsof -t -i:8083)
    if [ ! -z "$PID" ]; then
        echo "Found process listening on 8083 (PID $PID). Killing it..."
        kill $PID
    fi
fi
