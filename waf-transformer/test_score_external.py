import json
import time
import os
from ml_scorer.score_requests import score

threshold = 5.46  # Based on score analysis - optimal threshold
parsed_logs_path = "../parsed_logs.jsonl"

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

def score_last_request():
    """Score the last request from parsed_logs.jsonl"""
    last_line = get_last_line(parsed_logs_path)
    if not last_line:
        return None
    
    try:
        request = json.loads(last_line)
        req_score = score(request)
        if isinstance(req_score, list):
            req_score = req_score[0]
        
        status = "MALICIOUS" if req_score > threshold else "SAFE"
        print(f"New Request Scored: {req_score:.2f} - {status}")
        print(f"Request Details: {request['m']} {request['p']} from {request.get('s', 'unknown')}")
        return req_score, status
    except Exception as e:
        print(f"Error scoring request: {e}")
        return None

# Score the current last line first
print("Scoring current last request...")
score_last_request()
print("-" * 50)

# Monitor file for changes and score new requests
print("Monitoring parsed_logs.jsonl for new requests...")
print("Press Ctrl+C to stop monitoring\n")

last_file_size = 0
if os.path.exists(parsed_logs_path):
    last_file_size = os.path.getsize(parsed_logs_path)

try:
    while True:
        if os.path.exists(parsed_logs_path):
            current_size = os.path.getsize(parsed_logs_path)
            
            # Check if file has grown (new line added)
            if current_size > last_file_size:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] New log detected!")
                score_last_request()
                last_file_size = current_size
                print("-" * 50)
        
        time.sleep(1)  # Check every second
        
except KeyboardInterrupt:
    print("\nStopping log monitor...")
