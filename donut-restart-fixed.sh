#!/bin/bash

# Donut Tracker Server Restart Script
# This script ensures only ONE instance runs

cd /root/mcserver/donut-tracker/donut || {
    echo "$(date): ERROR: Cannot cd to server directory" >> /tmp/donut-cron-error.log
    exit 1
}

# Check if server is running
if pgrep -f "python3 server.py" > /dev/null; then
    echo "$(date): Server is already running (PID: $(pgrep -f 'python3 server.py'))" >> restart.log
    exit 0
fi

# Kill any old processes (cleanup)
pkill -f "python3 server.py" 2>/dev/null
sleep 2

# Double-check nothing is running
if pgrep -f "python3 server.py" > /dev/null; then
    echo "$(date): WARNING: Could not kill old process" >> restart.log
    exit 1
fi

# Start new server
echo "$(date): Starting fresh server instance..." >> restart.log
nohup python3 server.py > output.log 2>&1 &

# Wait and verify
sleep 5
if pgrep -f "python3 server.py" > /dev/null; then
    PID=$(pgrep -f "python3 server.py")
    echo "$(date): SUCCESS: Server started with PID: $PID" >> restart.log
else
    echo "$(date): FAILURE: Server did not start" >> restart.log
    echo "=== Last 10 lines of output.log ===" >> restart.log
    tail -10 output.log >> restart.log 2>/dev/null
fi
