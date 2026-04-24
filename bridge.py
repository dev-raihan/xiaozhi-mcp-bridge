import asyncio
import websockets
import json
import logging
import requests
import threading
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('xiaozhi_bridge')

HTTP_URL = "https://xiaozhi-mcp-server.skr4test.workers.dev/mcp"
xiaozhi_token = None
xiaozhi_ws_url = None
connected = False
reconnect_delay = 5
loop = None
loop_thread = None

def set_token(token):
    global xiaozhi_token, xiaozhi_ws_url
    xiaozhi_token = token
    if token.startswith('wss://'):
        xiaozhi_ws_url = token
    else:
        xiaozhi_ws_url = f"wss://api.xiaozhi.me/mcp/?token={token}"
    logger.info(f"Token set: {xiaozhi_ws_url[:50]}...")

async def handle_xiaozhi_message(message, ws):
    try:
        logger.info(f"Received message: {message[:200]}")
        data = json.loads(message)
        msg_type = data.get('type', '')
        
        if msg_type == 'hello':
            logger.info(f"Received hello from xiaozhi")
            return None
        
        elif msg_type == 'mcp':
            payload = data.get('payload', {})
            method = payload.get('method')
            msg_id = payload.get('id')
            params = payload.get('params', {})
            session_id = data.get('session_id', '')
            
            if method == 'initialize':
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "Xiaozhi Bridge", "version": "1.0.0"}
                }
                return {"session_id": session_id, "type": "mcp", "payload": {"jsonrpc": "2.0", "id": msg_id, "result": result}}
            
            elif method == 'tools/list':
                logger.info("Received tools/list request")
                try:
                    resp = requests.post(HTTP_URL, json={
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "id": msg_id,
                        "params": params
                    }, timeout=30)
                    http_data = resp.json()
                    tools_count = len(http_data.get('result', {}).get('tools', []))
                    logger.info(f"Sending {tools_count} tools to xiaozhi")
                    return {"session_id": session_id, "type": "mcp", "payload": {"jsonrpc": "2.0", "id": msg_id, "result": http_data.get('result', {})}}
                except Exception as e:
                    logger.error(f"tools/list error: {e}")
                    return {"session_id": session_id, "type": "mcp", "payload": {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(e)}}}
            
            elif method == 'tools/call':
                try:
                    resp = requests.post(HTTP_URL, json={
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "id": msg_id,
                        "params": params
                    }, timeout=30)
                    http_data = resp.json()
                    return {"session_id": session_id, "type": "mcp", "payload": {"jsonrpc": "2.0", "id": msg_id, "result": http_data.get('result', {})}}
                except Exception as e:
                    logger.error(f"tools/call error: {e}")
                    return {"session_id": session_id, "type": "mcp", "payload": {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32603, "message": str(e)}}}
            
            else:
                return {"session_id": session_id, "type": "mcp", "payload": {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}}
        
        return None
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return None

async def xiaozhi_connection():
    global connected, reconnect_delay
    
    while True:
        try:
            if not xiaozhi_ws_url:
                await asyncio.sleep(1)
                continue
            
            logger.info(f"Connecting to xiaozhi.me...")
            async with websockets.connect(xiaozhi_ws_url, ping_interval=20, ping_timeout=10) as ws:
                connected = True
                reconnect_delay = 5
                logger.info("Connected to xiaozhi.me!")
                
                await asyncio.sleep(0.5)
                
                try:
                    while True:
                        message = await ws.recv()
                        response = await handle_xiaozhi_message(message, ws)
                        if response:
                            await ws.send(json.dumps(response))
                except websockets.exceptions.ConnectionClosed:
                    logger.info("WebSocket closed by xiaozhi")
                
        except websockets.exceptions.ConnectionClosed as e:
            logger.warning(f"Connection closed: {e}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        
        connected = False
        logger.info(f"Reconnecting in {reconnect_delay} seconds...")
        await asyncio.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 2, 60)

def run_asyncio_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(xiaozhi_connection())

def start_connection():
    global loop_thread
    if loop_thread is None or not loop_thread.is_alive():
        loop_thread = threading.Thread(target=run_asyncio_loop, daemon=True)
        loop_thread.start()

def get_status():
    s = {
        "connected": connected,
        "token_configured": bool(xiaozhi_token)
    }
    s["status"] = "connected" if connected else ("connecting" if xiaozhi_token else "disconnected")
    return s