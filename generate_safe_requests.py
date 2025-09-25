#!/usr/bin/env python3
"""
Generate 10,000 safe/benign requests for model training
This script creates legitimate traffic patterns that should score low on anomaly detection
"""

import requests
import time
import random
import json
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost"
TOTAL_REQUESTS = 10000
CONCURRENT_THREADS = 10
DELAY_BETWEEN_BATCHES = 0.1  # seconds

# Safe request patterns
SAFE_ENDPOINTS = [
    "/",
    "/user/1", "/user/2", "/user/3", "/user/4", "/user/5",
    "/user/10", "/user/15", "/user/20", "/user/25", "/user/30",
    "/file/document.pdf", "/file/image.jpg", "/file/report.xlsx",
    "/file/readme.txt", "/file/config.json", "/file/data.csv",
    "/file/photo.png", "/file/video.mp4", "/file/audio.wav"
]

SAFE_POST_DATA = [
    {"username": "john_doe", "password": "password123"},
    {"username": "jane_smith", "password": "mypassword"},
    {"username": "admin", "password": "admin123"},
    {"username": "user123", "password": "userpass"},
    {"username": "testuser", "password": "test123"},
    {"username": "guest", "password": "guest"},
    {"username": "demo", "password": "demo123"},
    {"username": "alice", "password": "alice2024"},
    {"username": "bob", "password": "bobsecure"},
    {"username": "charlie", "password": "charlie456"}
]

SAFE_DATA_PAYLOADS = [
    {"name": "John Doe", "email": "john@example.com", "age": 30},
    {"product": "laptop", "price": 999.99, "category": "electronics"},
    {"title": "Meeting Notes", "content": "Discussed project timeline"},
    {"search": "python programming", "filter": "recent"},
    {"order_id": 12345, "status": "shipped", "tracking": "ABC123"},
    {"user_id": 100, "preferences": {"theme": "dark", "notifications": True}},
    {"message": "Hello World", "timestamp": "2024-09-26"},
    {"config": {"debug": False, "timeout": 30}},
    {"feedback": "Great service!", "rating": 5},
    {"update": {"profile_completed": True, "last_login": "2024-09-26"}}
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
]

class RequestGenerator:
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        
    def generate_safe_request(self):
        """Generate a single safe request"""
        request_type = random.choice(['GET', 'POST_LOGIN', 'POST_DATA'])
        
        if request_type == 'GET':
            return self._generate_safe_get()
        elif request_type == 'POST_LOGIN':
            return self._generate_safe_login()
        else:
            return self._generate_safe_post_data()
    
    def _generate_safe_get(self):
        """Generate safe GET request"""
        endpoint = random.choice(SAFE_ENDPOINTS)
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache'
        }
        
        return {
            'method': 'GET',
            'url': f"{BASE_URL}{endpoint}",
            'headers': headers,
            'timeout': 10
        }
    
    def _generate_safe_login(self):
        """Generate safe POST login request"""
        data = random.choice(SAFE_POST_DATA)
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        return {
            'method': 'POST',
            'url': f"{BASE_URL}/login",
            'headers': headers,
            'json': data,
            'timeout': 10
        }
    
    def _generate_safe_post_data(self):
        """Generate safe POST data request"""
        data = random.choice(SAFE_DATA_PAYLOADS)
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        return {
            'method': 'POST',
            'url': f"{BASE_URL}/data",
            'headers': headers,
            'json': data,
            'timeout': 10
        }
    
    def send_request(self, request_config):
        """Send a single request"""
        try:
            if request_config['method'] == 'GET':
                response = requests.get(
                    request_config['url'],
                    headers=request_config['headers'],
                    timeout=request_config['timeout']
                )
            else:  # POST
                response = requests.post(
                    request_config['url'],
                    headers=request_config['headers'],
                    json=request_config.get('json'),
                    timeout=request_config['timeout']
                )
            
            self.success_count += 1
            return {
                'status': 'success',
                'status_code': response.status_code,
                'request': request_config
            }
            
        except Exception as e:
            self.error_count += 1
            return {
                'status': 'error',
                'error': str(e),
                'request': request_config
            }
    
    def run_batch(self, batch_size):
        """Run a batch of requests"""
        requests_batch = []
        for _ in range(batch_size):
            req_config = self.generate_safe_request()
            requests_batch.append(req_config)
        
        results = []
        with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
            future_to_request = {
                executor.submit(self.send_request, req_config): req_config 
                for req_config in requests_batch
            }
            
            for future in as_completed(future_to_request):
                result = future.result()
                results.append(result)
        
        return results
    
    def print_progress(self, current, total):
        """Print progress bar"""
        progress = (current / total) * 100
        bar_length = 50
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        elapsed_time = time.time() - self.start_time
        if current > 0:
            estimated_total = elapsed_time * total / current
            remaining_time = estimated_total - elapsed_time
            eta = f"ETA: {remaining_time:.1f}s"
        else:
            eta = "ETA: --"
        
        print(f'\r🚀 Progress: |{bar}| {progress:.1f}% ({current}/{total}) '
              f'✅ Success: {self.success_count} ❌ Errors: {self.error_count} {eta}', end='')
    
    def generate_requests(self):
        """Main function to generate all requests"""
        print("🛡️ Safe Request Generator for WAF Model Training")
        print("=" * 60)
        print(f"📊 Target: {TOTAL_REQUESTS} safe requests")
        print(f"🌐 Server: {BASE_URL}")
        print(f"🧵 Threads: {CONCURRENT_THREADS}")
        print(f"⏱️  Batch delay: {DELAY_BETWEEN_BATCHES}s")
        print()
        
        # Test server connectivity
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            print(f"✅ Server is responding (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Server connection failed: {e}")
            print("Please make sure the webserver is running on port 3000")
            return
        
        print()
        print("🚀 Starting request generation...")
        
        self.start_time = time.time()
        batch_size = 100  # Requests per batch
        total_batches = TOTAL_REQUESTS // batch_size
        
        for batch_num in range(total_batches):
            # Run batch
            results = self.run_batch(batch_size)
            
            # Update progress
            current_requests = (batch_num + 1) * batch_size
            self.print_progress(current_requests, TOTAL_REQUESTS)
            
            # Small delay between batches to not overwhelm server
            if batch_num < total_batches - 1:
                time.sleep(DELAY_BETWEEN_BATCHES)
        
        # Handle remaining requests
        remaining = TOTAL_REQUESTS % batch_size
        if remaining > 0:
            results = self.run_batch(remaining)
            self.print_progress(TOTAL_REQUESTS, TOTAL_REQUESTS)
        
        print("\n")
        print("=" * 60)
        print("🎉 Request generation completed!")
        
        elapsed_time = time.time() - self.start_time
        requests_per_second = TOTAL_REQUESTS / elapsed_time
        
        print(f"📊 Summary:")
        print(f"   Total Requests: {TOTAL_REQUESTS}")
        print(f"   ✅ Successful: {self.success_count}")
        print(f"   ❌ Failed: {self.error_count}")
        print(f"   ⏱️  Total Time: {elapsed_time:.2f} seconds")
        print(f"   🚄 Rate: {requests_per_second:.1f} requests/second")
        
        success_rate = (self.success_count / TOTAL_REQUESTS) * 100
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate > 95:
            print("\n🎯 Excellent! Your server handled the load well.")
        elif success_rate > 85:
            print("\n👍 Good performance with acceptable error rate.")
        else:
            print("\n⚠️  High error rate detected. Check server capacity.")
        
        print("\n💡 Next steps:")
        print("   1. Check parsed_logs.jsonl for new entries")
        print("   2. Run your anomaly detection model")
        print("   3. Verify these requests score as SAFE/benign")
        print("   4. Compare with malicious request scores")

def main():
    generator = RequestGenerator()
    
    try:
        generator.generate_requests()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Generation stopped by user")
        print(f"📊 Partial results: {generator.success_count} successful, {generator.error_count} failed")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()