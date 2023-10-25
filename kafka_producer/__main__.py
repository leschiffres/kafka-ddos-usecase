import json
import time
from kafka import KafkaProducer, producer
import datetime
from ddos_detection.algorithm import advanced_instance, baseline_instance

KAFKA_TOPIC="api_requests"

if __name__ == "__main__":

    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    print("Kafka Producer Started.")

    stream = advanced_instance()
    # stream = baseline_instance()
    for i in range(len(stream)):
        data = {
            "requester_ip": stream[i],
            "request_received_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        producer.send(KAFKA_TOPIC, json.dumps(data).encode("utf-8"))

        time.sleep(0.1)
