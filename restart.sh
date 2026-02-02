#!/bin/bash

# Discord Bot Restart Script
cd /root/discord-bot || exit 1

# Kill old bot
pkill -f "node.*bot.js" 2>/dev/null
sleep 2

# Start bot
echo "$(date): 🔄 Restarting Discord bot..." >> bot.log
nohup node bot.js >> bot-output.log 2>&1 &

# Verify
sleep 5
if pgrep -f "node.*bot.js" > /dev/null; then
    PID=$(pgrep -f "node.*bot.js")
    echo "$(date): ✅ Bot started (PID: $PID)" >> bot.log
else
    echo "$(date): ❌ Bot failed to start" >> bot.log
    tail -10 bot-output.log >> bot.log 2>/dev/null
fi
