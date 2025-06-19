#!/bin/bash

# Chrome Debug with Your Profile - Copies your existing profile for debug mode
# This preserves all your logins and settings

echo "Starting Chrome with debug mode (copying your profile)"

# Kill existing Chrome processes
echo "Closing existing Chrome..."
pkill -f "Google Chrome" 2>/dev/null || true
sleep 2

# Setup debug profile with your existing data
ORIGINAL_PROFILE="$HOME/Library/Application Support/Google/Chrome"
DEBUG_PROFILE="$HOME/.chrome-debug-profile"

echo "Setting up debug profile with your existing data..."
rm -rf "$DEBUG_PROFILE"
cp -r "$ORIGINAL_PROFILE" "$DEBUG_PROFILE"

# Start Chrome with debug port using copied profile
echo "Starting Chrome with debug port 9222..."
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --remote-debugging-port=9222 \
    --user-data-dir="$DEBUG_PROFILE" \
    --no-first-run &

# Wait for Chrome to start
sleep 5

# Check if debug port is working
if nc -z localhost 9222 2>/dev/null; then
    echo "Chrome debug mode ready on port 9222"
    echo "All your logins and data are available!"
    echo "Now run: uv run specialized_agents/planning_agent.py"
else
    echo "❌ Debug port not accessible"
fi
