FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask gunicorn

COPY . /app/

EXPOSE 8000

CMD ["python", "-c", "
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'env_mcp': 'set' if os.environ.get('MCP_ENDPOINT') else 'NOT_SET',
        'env_http': 'set' if os.environ.get('HTTP_URL') else 'NOT_SET'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
"]