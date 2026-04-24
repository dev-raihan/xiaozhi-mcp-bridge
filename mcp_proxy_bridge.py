#!/usr/bin/env python3
"""
Xiaozhi MCP Bridge with Health Check
Connects to xiaozhi.me via WebSocket and proxies MCP requests to HTTP server
"""
import asyncio
import websockets
import requests
import sys
import os
import json
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler

load_dotenv()

MCP_ENDPOINT = os.environ.get('MCP_ENDPOINT') or sys.argv[2] if len(sys.argv) > 2 else None
HTTP_URL = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('HTTP_URL')
PORT = int(os.environ.get('PORT', 8000))

# Health check handler
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok", 
                "mcp_endpoint": "configured" if MCP_ENDPOINT else "not_set",
                "http_url": "configured" if HTTP_URL else "not_set"
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def start_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    print(f"Health server running on port {PORT}")
    return server

async def connect_to_xiaozhi():
    if not MCP_ENDPOINT:
        print("Warning: MCP_ENDPOINT not set. Set env var to connect to xiaozhi.")
        print("Run: set MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=xxx")
        return
    if not HTTP_URL:
        print("Warning: HTTP_URL not set.")
        return
    
    print(f"Connecting to xiaozhi: {MCP_ENDPOINT}")
    print(f"Proxying to HTTP: {HTTP_URL}")
    
    while True:
        try:
            async with websockets.connect(MCP_ENDPOINT) as ws:
                print("Connected to xiaozhi!")
                
                async for msg in ws:
                    print(f"→ Received: {msg[:100]}...")
                    
                    try:
                        req = json.loads(msg)
                        method = req.get('method')
                        params = req.get('params', {})
                        req_id = req.get('id')
                        
                        if method == 'tools/call':
                            tool_name = params.get('name')
                            tool_args = params.get('arguments', {})
                            
                            resp = requests.post(
                                HTTP_URL,
                                json={
                                    "jsonrpc": "2.0",
                                    "id": req_id,
                                    "method": method,
                                    "params": {"name": tool_name, "arguments": tool_args}
                                },
                                timeout=30
                            )
                            
                            result = resp.json()
                            await ws.send(json.dumps(result))
                            print(f"← Sent: {str(result)[:100]}...")
                            
                        elif method == 'tools/list':
                            resp = requests.post(
                                HTTP_URL,
                                json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": {}}
                            )
                            result = resp.json()
                            await ws.send(json.dumps(result))
                            
                    except Exception as e:
                        print(f"Error: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed, retrying in 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

async def main():
    # Start health server in background
    health_server = start_health_server()
    
    # Run both health server and websocket client
    await asyncio.gather(
        asyncio.to_thread(health_server.serve_forever),
        connect_to_xiaozhi() if MCP_ENDPOINT else asyncio.sleep(float('inf'))
    )

if __name__ == "__main__":
    asyncio.run(main())