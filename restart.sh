#!/bin/bash
cd /root/donut || exit 1

# Check if server is already running
if pgrep -f "python3 server.py" > /dev/null; then
    echo "$(date): Server already running" >> restart.log
    exit 0
fi

# Kill any old or stuck processes
pkill -f "python3 server.py" 2>/dev/null
sleep 2

# Start the server in the background
echo "$(date): Starting server..." >> restart.log
nohup python3 server.py > output.log 2>&1 &

# Verify it started
sleep 5
if pgrep -f "python3 server.py" > /dev/null; then
    echo "$(date): SUCCESS: Server started" >> restart.log
else
    echo "$(date): FAILURE: Server did not start" >> restart.log
    tail -5 output.log >> restart.log 2>/dev/null
fi
EOF

chmod +x restart.sh
