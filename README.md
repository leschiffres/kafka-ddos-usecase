# kafka-ddos-usecase

In this repo the goal is to implement a kafka example. Let's say we are in an organization 
where we want to be able to track down Denial-of-Service attacks, i.e. an overflow of requests from a pool of IPs. 
We decide to create a kafka topic where a service will post the received IPs in real time (`kafka_producer`) 
and another service will consume those messages (`kafka_consumer`) to be able to determine which IPs should be banned, 
because they are creating a huge flow of requests.

## The Kafka Setup

Start a docker container and find the kafka executables in the container with:
```bash
docker-compose up -d
docker exec -it kafka /bin/sh
cd opt/kafka_2.13-2.8.1/bin
```

then to start a kafka topic:

```bash
kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic api_requests
```

create a consumer group:
```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic api_requests --group ddos_detection_group
```

We initiate the kafka consumer with `poetry run python -m kafka_consumer` that checks for a DDoS attack on a rolling window basis.

We start a producer with `poetry run python -m kafka_producer` and the consumer running in the background should handle them accordingly. 


## The algorithm

Let's assume that we have We want to track down the IPs that send the most requests.
One idea would be to store for each IP the amount of requests it has done. However this is extremely innefficient and in some cases not possible to implement, because of limited memory (there can be billions of IPs sending requests). 

Thus, we want to be able to determine whether our system is under ddos attack using the least memory possible, while making sure that we parse the stream once or twice.

One efficient algorithm is the Alon-Matias-Szegedy Algorithm for which the authors got the Goedel Prize. 
The idea behind the algorithm is that given a stream of IP requests, we try to estimate the sum of the square of their cardinality.

e.g. if the stream is a,b,c,b,d,a,c,d,a,b,d,c,a,a,b then a appears 5 times, b appears 4 times, and c and d appear 3 times.
So the sum of square of those occurences is `5^2+4^2+3^2+3^2 = 59`

Ideally it would be great to store for each IP the number of total requests it has done. But sometimes this is not possible. The Alon-Matias-Szegedy algorithm instead stores a single number in memory that estimates this number.

Overall, we get a random IP from the stream and measure its frequency and at the end we estimate this by $n(2*freq-1)$ where $n$ is the size of the stream, and $freq$ the total requests by this IP. It can be proven that we if we do this many times, this method offers a good approximation of the number we want to estimate. For more details please see to the Mining Massive Datasets corresponding chapter.

## Restarting kafka stream from an outage

Let's say at some point the consumer went down for whatever reason.

To check the latest committed offset one can run:
```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group ddos_detection_group --describe
```

In the current consumer we commit an offset every 1000 messages. However one can go back in time by setting the offset accordingly. To check the offset for a specific message one can use `kcat`. For instance starting from the offset 500 we show the next 10 messages:

```bash
kcat -b localhost:9092 -t api_requests -o 500 -c 10
```

Before resetting the offset, make sure that the consumers are not running. To reset the ofset at a specific value e.g. 100 one can run the following command:

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group ddos_detection_group --topic api_requests --reset-offsets --to-offset 100 --execute
```
