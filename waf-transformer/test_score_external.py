from ml_scorer.score_requests import score

# Test individual requests with threshold logic
requests = [
  {
  "m": "GET",
  "p": "/search",
  "q": {
    "q": "dummy' OR '1'='1'; --",
    "page": "1"
  },
  "h": {
    "ua": "hacker-tool/1.0"
  },
  "s": "192.0.2.100",
  "b": {}
}
]

threshold = 5.46  # Based on score analysis - optimal threshold

for i, req in enumerate(requests):
    req_score = score(req)
    if isinstance(req_score, list):
        req_score = req_score[0]
    
    status = "MALICIOUS" if req_score > threshold else "SAFE"
    print(f"Request {i+1}: Score {req_score:.2f} - {status}")
