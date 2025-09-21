import re
import orjson
from confluent_kafka import Consumer, Producer

# Kafka config
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

# Precompiled regex
UUID_RE = re.compile(r"[0-9a-fA-F-]{36}")
NUM_RE = re.compile(r"\b\d+\b")
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")

def normalize_request(log_line: str):
    try:
        data = orjson.loads(log_line)

        method = data.get("method", "")
        path = data.get("path", "")
        headers = data.get("headers", {})

        # Normalize IDs/timestamps/numbers
        path = UUID_RE.sub("<UUID>", path)
        path = NUM_RE.sub("<NUM>", path)
        path = TS_RE.sub("<TS>", path)

        # Tokenization: method + path parts + header keys
        tokens = [method] + path.strip("/").split("/") + list(headers.keys())

        return {
            "tokens": tokens,
            "raw": data
        }
    except Exception:
        return None

print("Normalizer running...")

while True:
    msg = consumer.poll(1.0)
    if msg is None or msg.error():
        continue

    parsed = normalize_request(msg.value().decode("utf-8"))
    if parsed:
        producer.produce(PARSED_TOPIC, orjson.dumps(parsed))
        producer.flush()
