import orjson
from confluent_kafka import Consumer
import os

BOOTSTRAP_SERVERS = "localhost:29092"
PARSED_TOPIC = "api-logs-parsed"
OUTPUT_FILE = "parsed_logs.jsonl"

if not os.path.exists(OUTPUT_FILE):
    open(OUTPUT_FILE, "w").close()

consumer = Consumer({
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "group.id": "jsonl-writer",
    "auto.offset.reset": "earliest"
})
consumer.subscribe([PARSED_TOPIC])

print(f"📖 Listening on topic '{PARSED_TOPIC}', writing to {OUTPUT_FILE} ...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        try:
            data = orjson.loads(msg.value())
            line = orjson.dumps(data).decode("utf-8")

            with open(OUTPUT_FILE, "a") as f:
                f.write(line + "\n")

            print(f"Wrote log to {OUTPUT_FILE}")
        except Exception as e:
            print("Error processing message:", e)

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()
