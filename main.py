"""
Xiaozhi MCP Bridge - Connect external MCP tools to xiaozhi.me
"""

import os
import sys
import subprocess
import threading
import time
import signal
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

MCP_ENDPOINT = os.environ.get('MCP_ENDPOINT', '').strip()
MCP_URL = os.environ.get('MCP_URL', 'https://xiaozhi-mcp-server.skr4test.workers.dev/mcp').strip()
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)

bridge_process = None
bridge_running = False

def check_config():
    """Validate configuration"""
    errors = []
    endpoint = str(MCP_ENDPOINT) if MCP_ENDPOINT else ""
    
    if not MCP_ENDPOINT:
        errors.append("MCP_ENDPOINT is required")
    elif not endpoint.startswith('wss://'):
        errors.append("MCP_ENDPOINT must start with wss://")
    elif 'token=' not in endpoint:
        errors.append("MCP_ENDPOINT must contain 'token=' parameter")
    
    if not MCP_URL:
        errors.append("MCP_URL is required")
    
    return errors

def run_mcp_bridge():
    """Run the MCP bridge process"""
    global bridge_process, bridge_running
    
    print(f"\n{'='*50}")
    print("Starting Xiaozhi MCP Bridge...")
    print(f"MCP Endpoint: {MCP_ENDPOINT[:50]}..." if MCP_ENDPOINT else "MCP Endpoint: NOT SET")
    print(f"MCP URL: {MCP_URL}")
    print(f"{'='*50}\n")
    
    errors = check_config()
    if errors:
        print("[ERROR] Configuration errors:")
        for e in errors:
            print(f"  - {e}")
        return
    
    bridge_running = True
    
    while bridge_running:
        try:
            env = os.environ.copy()
            env['MCP_ENDPOINT'] = MCP_ENDPOINT
            env['MCP_URL'] = MCP_URL
            
            print("[INFO] Starting MCP pipe...")
            
            bridge_process = subprocess.Popen(
                [sys.executable, 'mcp_pipe.py', 'mcp_stdio_client.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in bridge_process.stdout:
                print(f"[MCP] {line.rstrip()}")
            
            bridge_process.wait()
            
        except Exception as e:
            print(f"[ERROR] Bridge error: {e}")
        
        if bridge_running:
            print("[INFO] Reconnecting in 5 seconds...")
            time.sleep(5)

def start_bridge_thread():
    """Start the bridge in a background thread"""
    thread = threading.Thread(target=run_mcp_bridge, daemon=True)
    thread.start()

@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'Xiaozhi MCP Bridge',
        'endpoint_configured': bool(MCP_ENDPOINT),
        'mcp_url': MCP_URL
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'bridge_running': bridge_running}), 200

@app.route('/status')
def status():
    return jsonify({
        'bridge_running': bridge_running,
        'endpoint_configured': bool(MCP_ENDPOINT),
        'mcp_url': MCP_URL
    })

def signal_handler(sig, frame):
    global bridge_running
    print("\n[INFO] Shutting down...")
    bridge_running = False
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start bridge on background thread
    start_bridge_thread()
    
    # Run Flask for health checks
    app.run(host='0.0.0.0', port=PORT)