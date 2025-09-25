#!/usr/bin/env python3
"""
WAF Transformer Score Analysis Tool
Helps determine safe vs malicious score thresholds
"""

from ml_scorer.score_requests import score
import json

def analyze_scores():
    print("🔍 WAF Transformer Score Analysis")
    print("=" * 60)
    
    # Test cases from your actual parsed logs
    test_cases = [
        {
            "name": "Normal GET Request",
            "type": "SAFE", 
            "request": {"m":"GET","p":"/","q":{},"h":{"ua":"curl/8.16.0","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        },
        {
            "name": "Normal POST with Data", 
            "type": "SAFE",
            "request": {"m":"POST","p":"/data","q":{},"h":{"ua":"PostmanRuntime/7.46.1","ct":"application/json","cl":"25","cookieKeys":[]},"s":"172.18.0.1","b":{"message":"Data received successfully"}}
        },
        {
            "name": "Favicon Request",
            "type": "SAFE", 
            "request": {"m":"GET","p":"/favicon.ico","q":{},"h":{"ua":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        },
        {
            "name": "Suspicious Query Parameter",
            "type": "SUSPICIOUS",
            "request": {"m":"GET","p":"/","q":{"ass":"gyat"},"h":{"ua":"PostmanRuntime/7.46.1","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        },
        {
            "name": "Profanity in Query", 
            "type": "SUSPICIOUS",
            "request": {"m":"GET","p":"/","q":{"madarchod":"123"},"h":{"ua":"Mozilla/5.0","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        },
        {
            "name": "XSS Attack Attempt",
            "type": "MALICIOUS", 
            "request": {"m":"GET","p":"/","q":{"q":"<script>alert(1)</script>"},"h":{"ua":"Mozilla/5.0","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        },
        {
            "name": "SQL Injection Attempt",
            "type": "MALICIOUS",
            "request": {"m":"GET","p":"/","q":{"id":"1' OR 1=1--"},"h":{"ua":"Mozilla/5.0","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        },
        {
            "name": "Admin Path Probing",
            "type": "MALICIOUS", 
            "request": {"m":"GET","p":"/admin","q":{},"h":{"ua":"python-requests/2.31.0","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        },
        {
            "name": "Long Query Parameter (Buffer Overflow)",
            "type": "MALICIOUS",
            "request": {"m":"GET","p":"/","q":{"q":"A"*1000},"h":{"ua":"Mozilla/5.0","ct":"","cl":"","cookieKeys":[]},"s":"172.18.0.1","b":{}}
        }
    ]
    
    scores_by_type = {"SAFE": [], "SUSPICIOUS": [], "MALICIOUS": []}
    
    print("📊 Testing Different Request Types:\n")
    
    for test_case in test_cases:
        try:
            request_score = score(test_case["request"])
            if isinstance(request_score, list):
                request_score = request_score[0]
                
            scores_by_type[test_case["type"]].append(request_score)
            
            # Color coding
            if test_case["type"] == "SAFE":
                color = "\033[92m"  # Green
            elif test_case["type"] == "SUSPICIOUS": 
                color = "\033[93m"  # Yellow
            else:
                color = "\033[91m"  # Red
            reset_color = "\033[0m"
            
            print(f"{color}{test_case['type']:<11}{reset_color} Score: {request_score:6.2f} - {test_case['name']}")
            
        except Exception as e:
            print(f"❌ Error scoring {test_case['name']}: {e}")
    
    # Analysis
    print("\n" + "=" * 60)
    print("📈 SCORE ANALYSIS:")
    print("-" * 60)
    
    for req_type, scores in scores_by_type.items():
        if scores:
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
            
            if req_type == "SAFE":
                color = "\033[92m"
            elif req_type == "SUSPICIOUS":
                color = "\033[93m" 
            else:
                color = "\033[91m"
            reset_color = "\033[0m"
            
            print(f"{color}{req_type:<11}{reset_color} Avg: {avg_score:5.2f} | Range: {min_score:5.2f} - {max_score:5.2f} | Count: {len(scores)}")
    
    # Recommendations
    all_safe = scores_by_type["SAFE"]
    all_malicious = scores_by_type["MALICIOUS"] 
    all_suspicious = scores_by_type["SUSPICIOUS"]
    
    print("\n" + "=" * 60)
    print("🎯 THRESHOLD RECOMMENDATIONS:")
    print("-" * 60)
    
    if all_safe and all_malicious:
        # Simplified threshold calculation
        all_scores = all_safe + all_malicious
        if all_suspicious:
            all_scores.extend(all_suspicious)
        
        median_score = sorted(all_scores)[len(all_scores)//2]
        
        print(f"✅ SAFE (Normal Traffic):     Score ≤ {median_score:.2f}")
        print(f"🚨 MALICIOUS (Block/Alert):   Score > {median_score:.2f}")
        print(f"📊 Optimal Threshold:         {median_score:.2f} (median of all scores)")
    
    print(f"\n💡 USAGE:")
    print(f"   - Monitor requests with high scores")
    print(f"   - Set alerts for scores above threshold") 
    print(f"   - Collect more data to refine thresholds")

if __name__ == "__main__":
    analyze_scores()