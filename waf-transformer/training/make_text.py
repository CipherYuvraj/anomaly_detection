# make_text.py
import json, sys, os

def as_text(r):
    q = "&".join(f"{k}={v}" for k,v in sorted(r.get("q",{}).items()))
    h = r.get("h",{})
    ua, ct, cl = h.get("ua",""), h.get("ct",""), h.get("cl","")
    ck = ",".join(h.get("cookieKeys",[]))
    # Handle body - convert dict to string if needed
    body = r.get("b","")
    if isinstance(body, dict):
        body = json.dumps(body, separators=(',', ':'))
    body = str(body)[:80]
    # ONE flat string, stable fields first
    return f'{r["m"]} {r["p"]} ? {q} UA={ua} CT={ct} CL={cl} CK={ck} B={body} S={r.get("s","")}'

# Read from file specified as argument or default to parsed_logs.jsonl
input_file = sys.argv[1] if len(sys.argv) > 1 else "../../parsed_logs.jsonl"

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        line_number = 0
        for line in f:
            line_number += 1
            line = line.strip()
            if line:  
                json_objects = []
                current_pos = 0
                
                while current_pos < len(line):
                    try:
                        decoder = json.JSONDecoder()
                        obj, idx = decoder.raw_decode(line, current_pos)
                        json_objects.append(obj)
                        current_pos = idx
                        # Skip any whitespace between objects
                        while current_pos < len(line) and line[current_pos].isspace():
                            current_pos += 1
                    except json.JSONDecodeError as e:
                        if not json_objects:  # If no objects parsed yet, it's a real error
                            print(f"Error parsing JSON on line {line_number}: {line[:100]}...", file=sys.stderr)
                            print(f"JSON Error: {e}", file=sys.stderr)
                        break
                
                # Process all parsed JSON objects
                for r in json_objects:
                    print(as_text(r))
except FileNotFoundError:
    print(f"Error: File {input_file} not found", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error reading file: {e}", file=sys.stderr)
    sys.exit(1)
