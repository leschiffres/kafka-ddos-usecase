import json
import time
from kafka import KafkaProducer, producer
import datetime
import numpy as np

KAFKA_TOPIC="api_requests"

if __name__ == "__main__":

    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    print("Kafka Producer Started.")

    # to showcase our example we create a sample of 1000 requests and we assume that there are 100 IPs sending requests
    # where 30% of the traffic comes from a pool of 10 IPs and the rest of 70% from 90 IPs.
    ddos_traffic = np.random.randint(0, 10, size=300).tolist()

    stream = np.random.randint(0, 90, size=700).tolist()

    stream.extend(ddos_traffic)
    np.random.shuffle(stream)
    

    for i in range(len(stream)):
        data = {
            "requester_ip": stream[i],
            "request_received_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        producer.send(KAFKA_TOPIC, json.dumps(data).encode("utf-8"))

        time.sleep(0.1)
