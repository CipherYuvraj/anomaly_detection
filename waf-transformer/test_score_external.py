import json
import time
import os
import threading
from flask import Flask, jsonify, render_template_string
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from ml_scorer.score_requests import score

threshold = 5.8
parsed_logs_path = "../parsed_logs.jsonl"

app = Flask(__name__, static_folder='../dashboard/public', static_url_path='/static')
app.config['SECRET_KEY'] = 'waf_dashboard_secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

recent_requests = []
stats = {
    'totalRequests': 0,
    'maliciousRequests': 0,
    'safeRequests': 0,
    'highestScore': 0.0,
    'averageScore': 0.0
}

all_scores = []

def get_last_line(file_path):
    """Get the last line from the file"""
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                return lines[-1].strip()
    except Exception as e:
        print(f"Error reading file: {e}")
    return None

def score_and_process_request(request_line):
    """Score a request and update dashboard data"""
    try:
        request = json.loads(request_line.strip())
        req_score = score(request)
        if isinstance(req_score, list):
            req_score = req_score[0]
        
        status = "MALICIOUS" if req_score > threshold else "SAFE"
        
        request_data = {
            'id': int(time.time() * 1000000),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'method': request.get('m', 'UNKNOWN'),
            'path': request.get('p', '/'),
            'source': request.get('s', 'unknown'),
            'score': round(float(req_score), 2),
            'status': status,
            'query': request.get('q', {}),
            'headers': request.get('h', {}),
            'body': request.get('b', {}),
            'isMalicious': req_score > threshold
        }
        
        stats['totalRequests'] += 1
        if status == 'MALICIOUS':
            stats['maliciousRequests'] += 1
        else:
            stats['safeRequests'] += 1
        
        if req_score > stats['highestScore']:
            stats['highestScore'] = round(float(req_score), 2)
        
        all_scores.append(req_score)
        stats['averageScore'] = round(sum(all_scores) / len(all_scores), 2)
        
        recent_requests.insert(0, request_data)
        if len(recent_requests) > 100:
            recent_requests.pop()
        
        socketio.emit('newRequest', request_data)
        socketio.emit('statsUpdate', {
            'totalRequests': stats['totalRequests'],
            'maliciousRequests': stats['maliciousRequests'],
            'safeRequests': stats['safeRequests'],
            'averageScore': stats['averageScore']
        })
        
        try:
            import requests
            requests.post('http://localhost:8080/api/update', 
                         json={
                             'request_data': request_data,
                             'stats': {
                                 'totalRequests': stats['totalRequests'],
                                 'maliciousRequests': stats['maliciousRequests'],
                                 'safeRequests': stats['safeRequests'],
                                 'averageScore': stats['averageScore']
                             }
                         }, timeout=1)
        except:
            pass  
        
        print(f"New Request Scored: {req_score:.2f} - {status}")
        print(f"Request Details: {request['m']} {request['p']} from {request.get('s', 'unknown')}")
        return req_score, status
    except Exception as e:
        print(f"Error scoring request: {e}")
        return None

def score_last_request():
    """Score the last request from parsed_logs.jsonl"""
    last_line = get_last_line(parsed_logs_path)
    if not last_line:
        return None
    return score_and_process_request(last_line)

@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    try:
        with open('../dashboard/public/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        try:
            with open('dashboard/public/index.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return """
            <html>
            <head><title>WAF Dashboard</title></head>
            <body>
            <h1>WAF Anomaly Detection Dashboard</h1>
            <p>Dashboard HTML file not found. The API endpoints are still available at:</p>
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

@socketio.on('connect')
def handle_connect():
    print('🔌 Client connected to dashboard')
    socketio.emit('initialData', {
        'stats': {
            'totalRequests': stats['totalRequests'],
            'maliciousRequests': stats['maliciousRequests'],
            'safeRequests': stats['safeRequests'],
            'averageScore': stats['averageScore']
        },
        'recentRequests': recent_requests[:20]
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('🔌 Client disconnected from dashboard')

def start_dashboard_server():
    """Start the Flask-SocketIO dashboard server"""
    print("🚀 Starting WAF Dashboard on http://localhost:4000")
    socketio.run(app, host='0.0.0.0', port=4000, debug=False, allow_unsafe_werkzeug=True)

def monitor_logs():
    """Monitor parsed_logs.jsonl for new entries"""
    print("Scoring current last request...")
    score_last_request()
    print("-" * 50)
    
    print("Monitoring parsed_logs.jsonl for new requests...")
    print("Press Ctrl+C to stop monitoring\n")

    last_file_size = 0
    if os.path.exists(parsed_logs_path):
        last_file_size = os.path.getsize(parsed_logs_path)

    try:
        while True:
            if os.path.exists(parsed_logs_path):
                current_size = os.path.getsize(parsed_logs_path)
                
                if current_size > last_file_size:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] New log detected!")
                    score_last_request()
                    last_file_size = current_size
                    print("-" * 50)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping log monitor...")

if __name__ == '__main__':
    print("🛡️ WAF Anomaly Detection System with Real-time Dashboard")
    print("=" * 60)
    
    dashboard_thread = threading.Thread(target=start_dashboard_server, daemon=True)
    dashboard_thread.start()
    
    time.sleep(2)
    
    monitor_logs()
