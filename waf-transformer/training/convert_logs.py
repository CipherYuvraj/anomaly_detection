import json
import sys

def as_text(r):
    q = "&".join(f"{k}={v}" for k,v in sorted(r.get("q",{}).items()))
    h = r.get("h",{})
    ua, ct, cl = h.get("ua",""), h.get("ct",""), h.get("cl","")
    ck = ",".join(h.get("cookieKeys",[]))
    body = r.get("b","")
    if isinstance(body, dict):
        body = json.dumps(body, separators=(',', ':'))
    body = str(body)[:80]
    return f'{r["m"]} {r["p"]} ? {q} UA={ua} CT={ct} CL={cl} CK={ck} B={body} S={r.get("s","")}'

with open('../../anomaly_detection/parsed_logs.jsonl', 'r', encoding='utf-8') as infile, open('ecom.txt', 'w', encoding='utf-8') as outfile:
    for line in infile:
        line = line.strip()
        if line:
            try:
                r = json.loads(line)
                outfile.write(as_text(r) + '\n')
            except:
                pass

# Create train/val splits
with open('ecom.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

split_idx = int(len(lines) * 0.9)
with open('train.txt', 'w', encoding='utf-8') as f:
    for line in lines[:split_idx]:
        f.write(line + '\n')
        
with open('val.txt', 'w', encoding='utf-8') as f:
    for line in lines[split_idx:]:
        f.write(line + '\n')

print(f'Created ecom.txt with {len(lines)} lines')
print(f'Created train.txt with {split_idx} lines')
print(f'Created val.txt with {len(lines) - split_idx} lines')