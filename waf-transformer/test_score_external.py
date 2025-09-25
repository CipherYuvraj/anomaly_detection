#!/usr/bin/env python3
"""
WAF Transformer Real-time Monitor with Dashboard Integration
Monitors parsed_logs.jsonl and sends results to the dashboard via WebSocket
Automatically removes malicious requests from the log file
"""

import json
import time
import os
import asyncio
import websockets
from ml_scorer.score_requests import score

# Configuration
threshold = 5.46  # Based on score analysis - optimal threshold
parsed_logs_path = "../parsed_logs.jsonl"
dashboard_ws_url = "ws://localhost:8765"

# Statistics
stats = {
    "safe_count": 0,
    "malicious_count": 0,
    "total_count": 0
}

# WebSocket connection
websocket_connection = None

async def connect_to_dashboard():
    """Connect to dashboard WebSocket server"""
    global websocket_connection
    try:
        websocket_connection = await websockets.connect(dashboard_ws_url)
        print("🔗 Connected to dashboard")
        await send_system_message("WAF Monitor connected successfully", "info")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to dashboard: {e}")
        websocket_connection = None
        return False

async def send_to_dashboard(message):
    """Send message to dashboard"""
    global websocket_connection
    if websocket_connection:
        try:
            await websocket_connection.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Dashboard connection lost")
            websocket_connection = None
        except Exception as e:
            print(f"❌ Error sending to dashboard: {e}")

async def send_request_score(request_data, score_value, status, action="monitored"):
    """Send request scoring result to dashboard"""
    message = {
        "type": "request_score",
        "data": {
            "method": request_data.get("m", "UNKNOWN"),
            "path": request_data.get("p", "/"),
            "source_ip": request_data.get("s", "unknown"),
            "score": round(score_value, 2),
            "status": status,
            "action": action,
            "timestamp": time.strftime("%H:%M:%S"),
            "query_params": request_data.get("q", {}),
            "user_agent": request_data.get("h", {}).get("ua", "Unknown")
        }
    }
    await send_to_dashboard(message)

async def send_system_message(message_text, msg_type="info"):
    """Send system message to dashboard"""
    message = {
        "type": "system",
        "message": message_text,
        "level": msg_type,
        "timestamp": time.strftime("%H:%M:%S")
    }
    await send_to_dashboard(message)

async def send_stats_update():
    """Send updated statistics to dashboard"""
    message = {
        "type": "stats_update",
        "data": {
            "safe_count": stats["safe_count"],
            "malicious_count": stats["malicious_count"], 
            "total_count": stats["total_count"],
            "timestamp": time.strftime("%H:%M:%S")
        }
    }
    await send_to_dashboard(message)

def get_all_requests():
    """Get all requests from the file"""
    if not os.path.exists(parsed_logs_path):
        return []
    
    try:
        with open(parsed_logs_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            # Validate JSON lines
            valid_lines = []
            for line in lines:
                try:
                    json.loads(line)
                    valid_lines.append(line)
                except json.JSONDecodeError:
                    continue
            return valid_lines
    except Exception as e:
        print(f"❌ Could not read file: {e}")
        return []

def remove_malicious_request(request_line):
    """Remove a malicious request from the log file"""
    try:
        # Read all lines
        all_lines = get_all_requests()
        
        # Remove the specific line
        if request_line in all_lines:
            all_lines.remove(request_line)
            
            # Write back to file with UTF-8 encoding
            with open(parsed_logs_path, 'w', encoding='utf-8') as f:
                for line in all_lines:
                    f.write(line + '\n')
            
            print(f"🗑️  Removed malicious request from log file")
            return True
        else:
            print("⚠️  Request not found in log file")
            return False
            
    except Exception as e:
        print(f"❌ Error removing malicious request: {e}")
        return False

def get_last_line():
    """Get the last line from the file"""
    lines = get_all_requests()
    # Find the last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line.strip()
    return None

async def score_last_request():
    """Score the last request from parsed_logs.jsonl"""
    last_line = get_last_line()
    if not last_line:
        return None
    
    try:
        # Parse JSON with better error handling
        request = json.loads(last_line)
        if not isinstance(request, dict):
            print(f"⚠️  Invalid request format: not a dictionary")
            return None
            
        req_score = score(request)
        if isinstance(req_score, list):
            req_score = req_score[0]
        
        # Update statistics
        stats["total_count"] += 1
        
        status = "MALICIOUS" if req_score > threshold else "SAFE"
        action = "monitored"
        
        if status == "MALICIOUS":
            stats["malicious_count"] += 1
            # Remove malicious request from file
            if remove_malicious_request(last_line):
                action = "deleted"
                await send_system_message(f"🚨 THREAT BLOCKED: {request['m']} {request['p']} (Score: {req_score:.2f})", "warning")
        else:
            stats["safe_count"] += 1
            await send_system_message(f"✅ Safe request: {request['m']} {request['p']} (Score: {req_score:.2f})", "info")
        
        # Send to console
        print(f"📊 Request Scored: {req_score:.2f} - {status}")
        print(f"   Details: {request['m']} {request['p']} from {request.get('s', 'unknown')}")
        if action == "deleted":
            print(f"   🗑️  MALICIOUS REQUEST REMOVED FROM LOG")
        
        # Send to dashboard
        await send_request_score(request, req_score, status, action)
        await send_stats_update()
        
        return req_score, status, action
        
    except Exception as e:
        print(f"❌ Error scoring request: {e}")
        await send_system_message(f"Error scoring request: {e}", "error")
        return None

async def main_monitor_loop():
    """Main monitoring loop"""
    print("🔥 WAF Transformer Real-time Monitor")
    print("=" * 50)
    
    # Try to connect to dashboard
    dashboard_connected = await connect_to_dashboard()
    if dashboard_connected:
        await send_system_message("WAF Transformer monitoring started", "info")
    
    # Score current last line first
    print("📊 Scoring current last request...")
    await score_last_request()
    print("-" * 50)
    
    # Monitor file for changes and score new requests
    print("👀 Monitoring parsed_logs.jsonl for new requests...")
    print("🎛️  Dashboard URL: http://localhost:8000")
    print("⌨️  Press Ctrl+C to stop monitoring\n")
    
    last_file_size = 0
    if os.path.exists(parsed_logs_path):
        last_file_size = os.path.getsize(parsed_logs_path)
    
    try:
        while True:
            # Reconnect to dashboard if disconnected
            if not websocket_connection:
                await asyncio.sleep(5)  # Wait before retrying
                dashboard_connected = await connect_to_dashboard()
            
            if os.path.exists(parsed_logs_path):
                current_size = os.path.getsize(parsed_logs_path)
                
                # Check if file has grown (new line added)
                if current_size > last_file_size:
                    print(f"🔔 [{time.strftime('%H:%M:%S')}] New log detected!")
                    result = await score_last_request()
                    last_file_size = os.path.getsize(parsed_logs_path)  # Update size after potential deletion
                    print("-" * 50)
            
            await asyncio.sleep(1)  # Check every second
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n🛑 Stopping WAF monitor...")
        if websocket_connection:
            try:
                await send_system_message("WAF Monitor disconnected", "warning")
                await websocket_connection.close()
            except Exception:
                pass  # Ignore errors during cleanup

if __name__ == "__main__":
    try:
        asyncio.run(main_monitor_loop())
    except KeyboardInterrupt:
        print("\n✅ WAF monitor stopped gracefully")
    except Exception as e:
        print(f"❌ Monitor error: {e}")
        import traceback
        traceback.print_exc()
