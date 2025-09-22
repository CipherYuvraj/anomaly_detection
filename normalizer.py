import re
import orjson
from confluent_kafka import Consumer, Producer

BOOTSTRAP_SERVERS = "localhost:29092"
RAW_TOPIC = "api-logs"
PARSED_TOPIC = "api-logs-parsed"

consumer = Consumer({
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "group.id": "normalizer",
    "auto.offset.reset": "earliest"
})
consumer.subscribe([RAW_TOPIC])

producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})

NUM_RE = re.compile(r"\b\d+\b")

def normalize_path(path: str) -> str:
    return NUM_RE.sub(":num", path)

def normalize_query(query):
    if not query:
        return {}
    if isinstance(query, dict):
        return {k: (":num" if isinstance(v, str) and v.isdigit() else v) for k, v in query.items()}
    if isinstance(query, str):
        norm = {}
        for kv in query.split("&"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                norm[k] = ":num" if v.isdigit() else v
        return norm
    return {}

def normalize_headers(headers: dict) -> dict:
    h = {}
    if not headers:
        return h

    # normalize keys to lowercase
    headers = {k.lower(): v for k, v in headers.items()}

    # User Agent
    if "user-agent" in headers:
        h["ua"] = headers["user-agent"]
    elif "ua" in headers:
        h["ua"] = headers["ua"]

    # Content-Type
    if "content-type" in headers:
        h["ct"] = headers["content-type"]
    elif "ct" in headers:
        h["ct"] = headers["ct"]

    # Content-Length
    if "content-length" in headers:
        h["cl"] = ":num"
    elif "cl" in headers:
        h["cl"] = ":num"

    # Cookie parsing
    if "cookie" in headers:
        cookie_keys = [kv.split("=")[0].strip() for kv in headers["cookie"].split(";") if "=" in kv]
        h["cookieKeys"] = cookie_keys
    elif "cookieKeys" in headers:
        h["cookieKeys"] = headers["cookieKeys"]

    return h



def normalize_request(log_line: str):
    try:
        data = orjson.loads(log_line)

        return {
            "m": data.get("method", ""),
            "p": normalize_path(data.get("path", "")),
            "q": normalize_query(data.get("query", {})),
            "h": normalize_headers(data.get("headers", {})),
            "s": data.get("remote_addr", ""),   
            "b": parse_body(data)               
        }
    except Exception as e:
        print("Normalize error:", e)
        return None


def parse_body(data: dict):
    body = data.get("body")
    if not body:
        return {}
    try:
        return orjson.loads(body) if isinstance(body, str) else body
    except Exception:
        return {"raw": body}


print("Normalizer running...")

while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue
    parsed = normalize_request(msg.value())
    if parsed:
        producer.produce(PARSED_TOPIC, orjson.dumps(parsed))
        producer.flush()