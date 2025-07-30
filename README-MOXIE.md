# Moxie Claude Wrapper - Setup Guide

This guide explains how to set up and use the Moxie Claude Wrapper, which brings Claude's intelligence to Moxie robots with emotion detection and TTSFM integration.

## First-Time Setup

### 1. Initial Authentication

Since this uses Claude CLI authentication, you need to authenticate once:

```bash
# Start the container with VNC access
docker-compose -f docker-compose.moxie.yml up -d

# Access the desktop environment:
# Option A: VNC client to localhost:5900 (password: moxie123)
# Option B: Web browser to http://localhost:6080

# In the desktop terminal:
cd /app
python3 auth.py
# Follow the authentication prompts
```

### 2. After Authentication

Once authenticated, the credentials are stored in the `claude-auth` volume.

```bash
# Restart the container
docker-compose -f docker-compose.moxie.yml restart moxie-claude

# Check if authentication is valid
docker logs moxie-claude
```

### 3. Enable Auto-Start (Optional)

To automatically start the server after authentication:

```bash
# Edit docker-compose.moxie.yml and set:
AUTO_START_SERVER=true

# Or use environment variable:
AUTO_START_SERVER=true docker-compose -f docker-compose.moxie.yml up -d
```

## OpenMoxie Integration

### 1. Update OpenMoxie Settings

In your OpenMoxie `settings.py`:

```python
# Point to Moxie Claude Wrapper instead of OpenAI
OPENAI_API_BASE = "http://moxie-claude:8000/v1"  # or your server IP
OPENAI_API_KEY = "not-needed-using-cli-auth"  # Can be any string
OPENAI_MODEL = "claude-3-5-sonnet-latest"

# Enable Moxie features
MOXIE_EMOTION_DETECTION = True
```

### 2. Test the Integration

```bash
# Test emotion detection
curl -X POST http://localhost:8000/v1/moxie/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I am so happy to see you!"}'

# Test chat with Moxie enhancements
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-latest",
    "messages": [{"role": "user", "content": "Tell me a happy story!"}]
  }'
```

## Features

### Emotion Detection
- Automatically detects emotions in Claude's responses
- Maps to Moxie animations (joy, sympathetic, thinking, etc.)
- Filters content for child-appropriateness

### TTSFM Integration
When `TTSFM_ENABLED=true`:
- Generates emotion-appropriate voice instructions
- Uses "sage" voice for all responses
- Coordinates with Moxie animations

### Moxie Commands
Responses include Moxie-specific commands:
- `cmd:animate:joy` - Happy animations
- `cmd:animate:sympathetic` - Caring expressions
- `cmd:animate:thinking` - Curious looks
- `cmd:animate:celebrate` - Excited movements
- `cmd:animate:hug` - Comforting gestures

## Deployment on Unraid

1. Copy files to your Unraid server
2. Build and run:
```bash
docker-compose -f docker-compose.moxie.yml up -d
```

3. First time: Complete authentication via VNC
4. Set container to auto-start

## Environment Variables

- `MOXIE_MODE` - Enable Moxie enhancements (default: true)
- `MOXIE_EMOTION_DETECTION` - Detect emotions (default: true)  
- `TTSFM_ENABLED` - Enable TTSFM integration (default: false)
- `TTSFM_ENDPOINT` - TTSFM service URL
- `AUTO_START_SERVER` - Auto-start after auth (default: false)
- `API_KEY` - Optional API key protection
- `DEBUG_MODE` - Enable debug logging

## Troubleshooting

### Authentication Issues
```bash
# Check auth status
docker exec moxie-claude python3 -c "from auth import get_claude_code_auth_info; print(get_claude_code_auth_info())"

# Re-authenticate
docker exec -it moxie-claude python3 auth.py
```

### Service Not Starting
```bash
# Check logs
docker logs moxie-claude

# Manually start inside container
docker exec -it moxie-claude python3 main.py
```

### VNC Connection Failed
- Ensure port 5900 is not blocked
- Try web access on port 6080 instead
- Check VNC password is "moxie123"