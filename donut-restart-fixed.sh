#!/bin/bash

# Donut Tracker Server Restart Script
# This script ensures only ONE instance runs

SERVER_DIR="/root/mcserver/donut-tracker/donut"
cd "$SERVER_DIR" || {
    echo "$(date): ERROR: Cannot cd to $SERVER_DIR" >> /tmp/donut-cron-error.log
    exit 1
}

# Function to check if port is responding
check_port() {
    timeout 2 bash -c "echo > /dev/tcp/localhost/5000" 2>/dev/null
    return $?
}

# Check if server process AND port are working
if pgrep -f "python3 server.py" > /dev/null && check_port; then
    echo "$(date): Server is already running and port 5000 is responding (PID: $(pgrep -f 'python3 server.py'))" >> restart.log
    exit 0
fi

# Kill any old processes (cleanup)
pkill -f "python3 server.py" 2>/dev/null
sleep 2

# Start new server
echo "$(date): Starting fresh server instance..." >> restart.log
nohup python3 server.py > output.log 2>&1 &

# Wait and verify
sleep 5
if pgrep -f "python3 server.py" > /dev/null && check_port; then
    PID=$(pgrep -f "python3 server.py")
    echo "$(date): SUCCESS: Server started with PID: $PID" >> restart.log
else
    echo "$(date): FAILURE: Server did not start or port not responding" >> restart.log
    echo "=== Last 10 lines of output.log ===" >> restart.log
    tail -10 output.log >> restart.log 2>/dev/null
fi
