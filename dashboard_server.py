import json
import time
import os
import threading
from flask import Flask, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__, static_folder='dashboard/public', static_url_path='/static')
app.config['SECRET_KEY'] = 'waf_dashboard_secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dashboard data
recent_requests = []
stats = {
    'totalRequests': 0,
    'maliciousRequests': 0,
    'safeRequests': 0,
    'averageScore': 0.0
}

@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    try:
        return send_file('dashboard/public/index.html')
    except FileNotFoundError:
        return """
        <html>
        <head><title>WAF Dashboard</title></head>
        <body>
        <h1>WAF Anomaly Detection Dashboard</h1>
        <p>Dashboard HTML file not found.</p>
        <p>The API endpoints are available at:</p>
        <ul>
        <li>/api/requests - Get recent requests</li>
        <li>/api/stats - Get statistics</li>
        </ul>
        </body>
        </html>
        """

@app.route('/api/requests')
def get_requests():
    return jsonify(recent_requests)

@app.route('/api/stats')
def get_stats():
    return jsonify(stats)

@app.route('/api/update', methods=['POST'])
def update_data():
    """Endpoint to receive updates from the ML scorer"""
    try:
        from flask import request
        data = request.get_json()
        
        if 'request_data' in data:
            recent_requests.insert(0, data['request_data'])
            if len(recent_requests) > 100:
                recent_requests.pop()
            socketio.emit('newRequest', data['request_data'])
        
        if 'stats' in data:
            stats.update(data['stats'])
            socketio.emit('statsUpdate', stats)
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('🔌 Client connected to dashboard')
    # Send initial data
    socketio.emit('initialData', {
        'stats': stats,
        'recentRequests': recent_requests[:20]
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('🔌 Client disconnected from dashboard')

if __name__ == '__main__':
    print("🚀 Starting WAF Dashboard Server on http://localhost:8080")
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)