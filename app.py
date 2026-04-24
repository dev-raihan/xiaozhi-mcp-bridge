from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)

MCP_ENDPOINT = os.environ.get('MCP_ENDPOINT', '')
HTTP_URL = os.environ.get('HTTP_URL', 'https://xiaozhi-mcp-server.skr4test.workers.dev/mcp')
PORT = int(os.environ.get('PORT', 10000))

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "mcp_endpoint_configured": bool(MCP_ENDPOINT),
        "http_url": HTTP_URL
    })

@app.route('/mcp', methods=['GET', 'POST'])
def mcp_endpoint():
    if request.method == 'GET':
        return jsonify({
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Xiaozhi Bridge", "version": "1.0.0"}
            }
        })
    
    body = request.json
    method = body.get('method')
    params = body.get('params', {})
    req_id = body.get('id')
    
    if method == 'tools/list':
        resp = requests.post(HTTP_URL, json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": {}}, timeout=30)
        return jsonify(resp.json())
    
    if method == 'tools/call':
        tool_name = params.get('name')
        tool_args = params.get('arguments', {})
        resp = requests.post(
            HTTP_URL,
            json={"jsonrpc": "2.0", "id": req_id, "method": method, "params": {"name": tool_name, "arguments": tool_args}},
            timeout=30
        )
        return jsonify(resp.json())
    
    return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)