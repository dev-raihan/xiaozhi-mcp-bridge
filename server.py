#!/usr/bin/env python3
"""
Xiaozhi MCP Bridge - Simple Health Server Version
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get('PORT', '8000'))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "mcp_endpoint": os.environ.get('MCP_ENDPOINT', 'NOT SET'),
                "http_url": os.environ.get('HTTP_URL', 'NOT SET')
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

print(f"Starting health server on port {PORT}")
print(f"MCP_ENDPOINT: {os.environ.get('MCP_ENDPOINT', 'NOT SET')}")
print(f"HTTP_URL: {os.environ.get('HTTP_URL', 'NOT SET')}")

server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
print(f"Server running at http://0.0.0.0:{PORT}/health")
server.serve_forever()