import json
from kafka import KafkaConsumer, TopicPartition
from os import environ

import time

KAFKA_TOPIC = "api_requests"
KAFKA_CONSUMER_GROUP_ID = "ddos_detection_group"

WINDOW = 100
THRESHOLD = 1000 # random value for the sake of simplicity

if __name__ == "__main__":

    kafka_configurations = {
        'bootstrap_servers':"localhost:9092",
        'group_id':KAFKA_CONSUMER_GROUP_ID,
        'auto_offset_reset':'earliest'
    }

    consumer=KafkaConsumer(**kafka_configurations)

    print("Started Consumer in Consumer Group")

    topic_partition = TopicPartition(KAFKA_TOPIC, 0)
    consumer.assign([topic_partition])
    committed_offset = consumer.position(topic_partition)
    consumer.seek(topic_partition, committed_offset)

    # important for the algorithm
    element, cardinality = None, None
    
    iterator = 0
    while True:
        for message in consumer:
            msg = json.loads(message.value.decode())
            print(msg)
            current_ip = msg['requester_ip']
            if iterator == 0:
                element = current_ip
                cardinality = 1
            else:

                if element == current_ip:
                    cardinality += 1

                # once we reach the window threshold we check the estimator against the threshold
                # to check if we are under DDoS attack
                if iterator > WINDOW:
                    estimator = WINDOW*(2*cardinality-1)
                    print("Estimator: ", estimator)
                    if estimator > THRESHOLD:
                        print("We are under DDoS Attack")
                    
                    # reset iterator
                    iterator = -1
                    element, cardinality = None, None

                    # we commit the offset once the window surpasses
                    consumer.commit()
                    print("Committed Offset.")
            iterator += 1
        time.sleep(0.01)
