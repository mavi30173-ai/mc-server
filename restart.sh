#!/bin/bash

# Discord Webhook Relay Restart Script
# Fixed for Node.js relay on port 3000

SERVER_DIR="/root/webhook-relay"
cd "$SERVER_DIR" || {
    echo "$(date): ERROR: Cannot cd to $SERVER_DIR" >> /tmp/relay-error.log
    exit 1
}

# Function to check if port 3000 is responding
check_port() {
    timeout 2 bash -c "echo > /dev/tcp/localhost/3000" 2>/dev/null
    return $?
}

# Check if Node.js process AND port are working
if pgrep -f "node.*index.js" > /dev/null && check_port; then
    echo "$(date): ✅ Relay is already running on port 3000 (PID: $(pgrep -f 'node.*index.js'))" >> restart.log
    exit 0
fi

# Kill any old processes (cleanup)
echo "$(date): 🔴 Killing old relay processes..." >> restart.log
pkill -f "node.*index.js" 2>/dev/null
sleep 2

# Start new relay server
echo "$(date): 🟢 Starting fresh relay instance..." >> restart.log
nohup node index.js > output.log 2>&1 &

# Wait and verify
sleep 5
if pgrep -f "node.*index.js" > /dev/null && check_port; then
    PID=$(pgrep -f "node.*index.js")
    echo "$(date): ✅ SUCCESS: Relay started with PID: $PID" >> restart.log
    echo "$(date): ✅ Relay URL: http://$(curl -s ifconfig.me):3000/webhook" >> restart.log
else
    echo "$(date): ❌ FAILURE: Relay did not start or port not responding" >> restart.log
    echo "=== Last 10 lines of output.log ===" >> restart.log
    tail -10 output.log >> restart.log 2>/dev/null
    echo "=== Trying to see what's wrong ===" >> restart.log
    ps aux | grep node >> restart.log 2>/dev/null
    netstat -tulpn | grep 3000 >> restart.log 2>/dev/null
fi
