# make_text.py
import json, sys
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
for line in sys.stdin:
    r=json.loads(line); print(as_text(r))
