#!/bin/bash

echo "=================================="
echo "Moxie Claude Wrapper Startup"
echo "=================================="

# Check if Claude is already authenticated
if python3 -c "from auth import validate_claude_code_auth; valid, _ = validate_claude_code_auth(); exit(0 if valid else 1)"; then
    echo "✅ Claude authentication is valid"
    
    # If AUTO_START_SERVER is true, start the server automatically
    if [ "$AUTO_START_SERVER" = "true" ]; then
        echo "Starting Moxie Claude Wrapper server..."
        exec python3 main.py
    else
        echo ""
        echo "Authentication is valid. You can now:"
        echo "1. Start the server manually: python3 main.py"
        echo "2. Or set AUTO_START_SERVER=true to start automatically"
        echo ""
        # Keep container running
        tail -f /dev/null
    fi
else
    echo "❌ Claude authentication required"
    echo ""
    echo "Please complete authentication:"
    echo "1. Connect via VNC (port 5900) or web browser (port 6080)"
    echo "2. Open a terminal in the desktop"
    echo "3. Run: cd /app && python3 auth.py"
    echo "4. Complete the authentication flow"
    echo "5. Restart the container or run: python3 main.py"
    echo ""
    echo "After authentication, you can set AUTO_START_SERVER=true"
    echo "to automatically start the server on container restart."
    echo ""
    
    # Start desktop environment for authentication
    exec /startup.sh
fi