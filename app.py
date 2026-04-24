from flask import Flask, jsonify
import os
import asyncio
import threading
import time
import signal
import sys

app = Flask(__name__)

MCP_ENDPOINT = os.environ.get('MCP_ENDPOINT', '')
MCP_URL = os.environ.get('MCP_URL', 'https://xiaozhi-mcp-server.skr4test.workers.dev/mcp')

connected = False
last_activity = None

def run_bridge():
    import subprocess
    import os
    
    while True:
        try:
            env = os.environ.copy()
            env['MCP_ENDPOINT'] = MCP_ENDPOINT
            env['MCP_URL'] = MCP_URL
            
            process = subprocess.Popen(
                [sys.executable, 'mcp_pipe.py', 'mcp_stdio_client.py'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.wait()
        except Exception as e:
            print(f"Bridge error: {e}")
        time.sleep(5)

bridge_thread = None

def start_bridge():
    global bridge_thread, connected
    if MCP_ENDPOINT:
        connected = True
        bridge_thread = threading.Thread(target=run_bridge, daemon=True)
        bridge_thread.start()

@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'connected': connected,
        'mcp_endpoint': 'configured' if MCP_ENDPOINT else 'not_set'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    if MCP_ENDPOINT:
        start_bridge()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))