"""
Xiaozhi MCP Bridge - Connect external MCP tools to xiaozhi.me

Usage:
    1. Copy .env.example to .env
    2. Edit .env with your tokens
    3. Run: python app.py

Environment Variables (set in .env):
    MCP_ENDPOINT   - xiaozhi.me WebSocket endpoint (wss://api.xiaozhi.me/mcp/?token=...)
    MCP_URL        - Your MCP server URL (optional, default provided)
    PORT           - Server port (default: 10000)
"""

import os
import sys
import asyncio
import subprocess
import threading
import time
import signal
from dotenv import load_dotenv

load_dotenv()

MCP_ENDPOINT = os.environ.get('MCP_ENDPOINT', '').strip()
MCP_URL = os.environ.get('MCP_URL', 'https://xiaozhi-mcp-server.skr4test.workers.dev/mcp').strip()
PORT = int(os.environ.get('PORT', 10000))

def check_config():
    """Validate configuration"""
    errors = []
    
    endpoint = str(MCP_ENDPOINT) if MCP_ENDPOINT else ""
    
    if not MCP_ENDPOINT:
        errors.append("MCP_ENDPOINT is required. Get it from xiaozhi.me dashboard")
    elif not endpoint.startswith('wss://'):
        errors.append("MCP_ENDPOINT must start with wss://")
    elif 'token=' not in endpoint:
        errors.append("MCP_ENDPOINT must contain 'token=' parameter")
    
    if not MCP_URL:
        errors.append("MCP_URL is required")
    
    return errors

def run_mcp_bridge():
    """Run the MCP bridge in a loop"""
    print(f"\n{'='*50}")
    print("Starting Xiaozhi MCP Bridge...")
    print(f"{'='*50}")
    print(f"MCP Endpoint: {MCP_ENDPOINT[:50]}..." if MCP_ENDPOINT else "MCP Endpoint: NOT SET")
    print(f"MCP URL: {MCP_URL}")
    print(f"Port: {PORT}")
    print(f"{'='*50}\n")
    
    while True:
        try:
            env = os.environ.copy()
            env['MCP_ENDPOINT'] = MCP_ENDPOINT
            env['MCP_URL'] = MCP_URL
            
            print("Starting MCP pipe...")
            
            process = subprocess.Popen(
                [sys.executable, 'mcp_pipe.py', 'mcp_stdio_client.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                print(f"[MCP] {line.rstrip()}")
            
            process.wait()
            
        except Exception as e:
            print(f"[ERROR] Bridge error: {e}")
        
        print("[INFO] Reconnecting in 5 seconds...")
        time.sleep(5)

def signal_handler(sig, frame):
    print("\n[INFO] Shutting down...")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    errors = check_config()
    if errors:
        print("\n[ERROR] Configuration errors:")
        for e in errors:
            print(f"  - {e}")
        print("\n[INFO] Please copy .env.example to .env and configure your tokens")
        sys.exit(1)
    
    run_mcp_bridge()
