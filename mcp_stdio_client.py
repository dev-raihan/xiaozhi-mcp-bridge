"""
Bridge xiaozhi WebSocket MCP protocol to HTTP MCP server
Handles both wrapped and unwrapped MCP message formats
"""
import sys
import json
import os
import requests

MCP_URL = os.environ.get('MCP_URL', '')
if not MCP_URL:
    print("Error: MCP_URL not set", file=sys.stderr)
    sys.exit(1)

def forward_request(method, params=None, msg_id=None):
    payload = {"jsonrpc": "2.0", "method": method, "id": msg_id or 1}
    if params:
        payload["params"] = params
    resp = requests.post(MCP_URL, json=payload, timeout=30)
    return resp.json()

def handle_message(msg):
    """Handle MCP message - may be wrapped or unwrapped"""
    session_id = None
    
    # Check if wrapped format: {"type":"mcp","payload":{...},"session_id":"..."}
    if "payload" in msg and "type" in msg:
        payload = msg.get("payload", {})
        session_id = msg.get("session_id")
        msg_id = payload.get("id")
        params = payload.get("params", {})
        method = payload.get("method")
    else:
        # Unwrapped format: {"jsonrpc":"2.0","method":"...","id":...}
        payload = msg
        msg_id = msg.get("id")
        params = msg.get("params", {})
        method = msg.get("method")
    
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "Xiaozhi Bridge", "version": "1.0.0"}}
        return {"id": msg_id, "jsonrpc": "2.0", "result": result}
    
    elif method in ("tools/list", "tools/call"):
        http_resp = forward_request(method, params, msg_id)
        result = http_resp.get("result", {})
        error = http_resp.get("error")
        if error:
            return {"id": msg_id, "jsonrpc": "2.0", "error": error}
        return {"id": msg_id, "jsonrpc": "2.0", "result": result}
    
    elif method == "ping":
        return {"id": msg_id, "jsonrpc": "2.0", "result": {}}
    
    else:
        return {"id": msg_id, "jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown: {method}"}}

while True:
    line = sys.stdin.readline()
    if not line:
        break
    
    try:
        msg = json.loads(line.strip())
    except json.JSONDecodeError:
        continue
    
    # Skip non-MCP messages (like hello)
    if msg.get("type") == "hello" or "method" not in msg:
        continue
    
    response = handle_message(msg)
    print(json.dumps(response), flush=True)