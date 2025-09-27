import json
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))

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

input_file = os.path.join(root_dir, 'parsed_logs.jsonl')
output_file = os.path.join(script_dir, 'ecom.txt')

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        line = line.strip()
        if line:
            try:
                r = json.loads(line)
                outfile.write(as_text(r) + '\n')
            except:
                pass

ecom_file = os.path.join(script_dir, 'ecom.txt')
train_file = os.path.join(script_dir, 'train.txt')
val_file = os.path.join(script_dir, 'val.txt')

with open(ecom_file, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

split_idx = int(len(lines) * 0.9)
with open(train_file, 'w', encoding='utf-8') as f:
    for line in lines[:split_idx]:
        f.write(line + '\n')
        
with open(val_file, 'w', encoding='utf-8') as f:
    for line in lines[split_idx:]:
        f.write(line + '\n')

print(f'Created ecom.txt with {len(lines)} lines')
print(f'Created train.txt with {split_idx} lines')
print(f'Created val.txt with {len(lines) - split_idx} lines')