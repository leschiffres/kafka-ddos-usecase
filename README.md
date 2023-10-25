# kafka-ddos-usecase

In this repo the goal is to implement a kafka example. Let's say we are in an organization 
where we want to be able to track down Denial-of-Service attacks, i.e. an overflow of requests from a pool of IPs. 
We decide to create a kafka topic where a service will post the received IPs in real time (`kafka_producer`) 
and another service will consume those messages (`kafka_consumer`) to be able to determine which IPs should be banned, 
because they are creating a huge flow of requests.

## The algorithm

Let's assume that we have We want to track down the IPs that send the most requests.
One idea would be to store for each IP the amount of requests it has done. However this is extremely innefficient and in some cases not possible to implement, because of limited memory (there can be billions of IPs sending requests). 

Thus, we want to be able to determine whether our system is under ddos attack using the least memory possible, while making sure that we parse the stream once or twice.

One efficient algorithm is the Alon-Matias-Szegedy Algorithm for which the authors got the Goedel Prize. 
Ideally given a stream of IPs, we would know the number of requests of all IPs and sum the square of their cardinality.
To do so we would have to store for each IP the number of total requests. Instead the algorithm stores a single number in memory
and tries to estimate the sum of square of frequencies.

e.g. if the stream is a,b,c,b,d,a,c,d,a,b,d,c,a,a,b then a appears 5 times, b appears 4 times, and c and d appear 3 times.
So the sum of square of those occurences is `5^2+4^2+3^2+3^2 = 59`

So we can see based on this number how normal traffic looks like and when it spikes that should correspond to a DDoS attack.

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

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group ddos_detection_group --topic api_requests --reset-offsets --to-offset 100 --dry-run
```

To reset the offset to a datetime

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group ddos_detection_group --reset-offsets --to-datetime 2023-10-25T00:00:00.000 --topic api_requests --execute
```