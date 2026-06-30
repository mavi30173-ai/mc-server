#!/bin/bash
cd /root/upload-server || exit 1

# Activate virtual environment
source venv/bin/activate

# Check if upload_server is already running
if pgrep -f "upload_server.py" > /dev/null; then
    echo "$(date): Upload server already running" >> logs/restart.log
    exit 0
fi

# Kill any old processes
pkill -f "upload_server.py" 2>/dev/null
sleep 2

# Start the server
echo "$(date): Starting upload server..." >> logs/restart.log
nohup python3 upload_server.py > logs/output.log 2>&1 &

# Verify it started
sleep 3
if pgrep -f "upload_server.py" > /dev/null; then
    echo "$(date): SUCCESS: Upload server started" >> logs/restart.log
else
    echo "$(date): FAILURE: Upload server did not start" >> logs/restart.log
    tail -5 logs/output.log >> logs/restart.log 2>/dev/null
fi
