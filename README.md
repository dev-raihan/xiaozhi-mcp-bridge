# Xiaozhi MCP Bridge

MCP Bridge for connecting to xiaozhi.me - Deploy on Render

## Quick Deploy on Render

1. Push to GitHub
2. Connect to render.com as Python web service
3. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Set env vars:
   - MCP_ENDPOINT = your xiaozhi token
   - HTTP_URL = https://xiaozhi-mcp-server.skr4test.workers.dev/mcp
   - PORT = 10000