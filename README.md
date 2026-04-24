# Xiaozhi MCP Bridge

Connect external MCP servers to xiaozhi.me to extend your AI assistant's capabilities with custom tools.

## Features

- Connects to xiaozhi.me via WebSocket
- Proxies MCP requests to your HTTP MCP server
- Supports all standard MCP methods (initialize, tools/list, tools/call)
- Auto-reconnect on connection loss
- Easy configuration via `.env` file

## Prerequisites

- Python 3.8+
- xiaozhi.me account with MCP access enabled
- An MCP server (HTTP endpoint)

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/dev-raihan/xiaozhi-mcp-bridge.git
cd xiaozhi-mcp-bridge
pip install -r requirements.txt
```

### 2. Configure

Copy the example env file and edit it:

```bash
cp .env.example .env
```

Edit `.env` with your tokens:

```env
# xiaozhi.me MCP endpoint (from xiaozhi.me dashboard -> MCP Access Point)
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=YOUR_TOKEN_HERE

# Your MCP server URL
MCP_URL=https://your-mcp-server.com/mcp

# Server port (optional, default: 10000)
PORT=10000
```

### 3. Run

```bash
python app.py
```

You should see:
```
==================================================
Starting Xiaozhi MCP Bridge...
==================================================
MCP Endpoint: wss://api.xiaozhi.me/mcp/?token=eyJ...
MCP URL: https://your-mcp-server.com/mcp
Port: 10000
==================================================

Starting MCP pipe...
```

## Available Tools (Default MCP Server)

Your bridge comes with these tools when using the default MCP server:

| Tool | Description |
|------|-------------|
| `weather` | Get current weather for any city |
| `web_search` | Search the web for current information |
| `wikipedia` | Search Wikipedia for factual information |
| `joke` | Get a random joke |
| `number_fact` | Get interesting trivia about a number |
| `history_today` | Major events that happened today in history |
| `crypto_price` | Get cryptocurrency prices in USD |
| `currency_convert` | Convert between world currencies |
| `air_quality` | Get air pollution/AQI for a city |
| `send_telegram_message` | Send notification via Telegram |
| `calculator` | Mathematical calculations |

## Deploy to Render

### 1. Push to GitHub

```bash
git add .
git commit -m "Setup xiaozhi MCP bridge"
git push origin main
```

### 2. Deploy on Render

1. Go to [render.com](https://render.com)
2. Connect your GitHub repo
3. Create **Web Service**
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Add Environment Variables:
   - `MCP_ENDPOINT` = your xiaozhi token
   - `MCP_URL` = your MCP server URL
   - `PORT` = `10000`
6. Deploy!

### 3. Keep Awake (Free Tier)

Render free tier sleeps after 15 minutes. Use UptimeRobot:

1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Add new monitor → **HTTPS monitor**
3. Enter your Render URL
4. Set check interval to **5 minutes**

## Architecture

```
┌─────────────┐      WebSocket       ┌──────────────┐
│   xiaozhi   │◄──────────────────► │ xiaozhi-mcp- │
│     .me     │                     │   bridge     │
└─────────────┘                     └──────┬───────┘
                                             │
                                             │ HTTP
                                             ▼
                                    ┌──────────────┐
                                    │ Your MCP     │
                                    │ Server       │
                                    └──────────────┘
```

## Project Structure

```
xiaozhi-mcp-bridge/
├── app.py              # Main entry point
├── mcp_pipe.py         # WebSocket bridge
├── mcp_stdio_client.py # MCP protocol handler
├── requirements.txt    # Python dependencies
├── .env.example       # Configuration template
└── .env                # Your configuration (create from .env.example)
```

## Troubleshooting

### "MCP_ENDPOINT is required"
- Copy `.env.example` to `.env`
- Add your xiaozhi token to `MCP_ENDPOINT`

### "Process has ended output"
- Your MCP server might not be responding
- Check if `MCP_URL` is correct and accessible
- Test your MCP server manually with:
  ```bash
  curl -X POST https://your-mcp-server.com/mcp \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
  ```

### Tools not showing in xiaozhi
- Restart the bridge
- Check console logs for errors
- Verify your MCP server is returning tools

## License

MIT