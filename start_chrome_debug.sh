#!/bin/bash

# Chrome Debug with Your Profile - Copies your existing profile for debug mode
# This preserves all your logins and settings

echo "Starting Chrome with debug mode (copying your profile)"

# Detect operating system
OS=$(uname -s)

# # Kill existing Chrome processes
# echo "Closing existing Chrome..."
# case $OS in
#     Darwin*)
#         pkill -f "Google Chrome" 2>/dev/null || true
#         ;;
#     MINGW*|CYGWIN*|MSYS*)
#         taskkill //F //IM chrome.exe 2>/dev/null || true
#         ;;
# esac
# sleep 2

# Setup debug profile with OS-specific paths
case $OS in
    Darwin*)
        echo "Detected macOS"
        ORIGINAL_PROFILE="$HOME/Library/Application Support/Google/Chrome"
        DEBUG_PROFILE="$HOME/.chrome-debug-profile"
        CHROME_BINARY="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ;;
    MINGW*|CYGWIN*|MSYS*)
        echo "Detected Windows"
        ORIGINAL_PROFILE="$USERPROFILE/AppData/Local/Google/Chrome/User Data"
        DEBUG_PROFILE="$USERPROFILE/.chrome-debug-profile"
        CHROME_BINARY="/c/Program Files/Google/Chrome/Application/chrome.exe"
        # Alternative Windows path
        if [ ! -f "$CHROME_BINARY" ]; then
            CHROME_BINARY="/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        fi
        ;;
    *)
        echo "Unsupported operating system: $OS"
        exit 1
        ;;
esac

echo "Setting up debug profile with your existing data..."
rm -rf "$DEBUG_PROFILE"
cp -r "$ORIGINAL_PROFILE" "$DEBUG_PROFILE"

# Start Chrome with debug port using copied profile
echo "Starting Chrome with debug port 9222..."
"$CHROME_BINARY" \
    --remote-debugging-port=9222 \
    --user-data-dir="$DEBUG_PROFILE" \
    --no-first-run \
    --new-window &

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
