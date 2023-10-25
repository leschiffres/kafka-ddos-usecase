# Kafka

# Installation

Locate the kafka folder with all executables.
```bash
docker-compose up -d
docker exec -it kafka /bin/sh
cd opt/kafka_2.13-2.8.1/bin
```

## Kafka topics

```bash
kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic first_kafka_topic
# list all kafka topics
kafka-topics.sh --list --zookeeper zookeeper:2181
# list partitions and replicas
kafka-topics.sh --describe --zookeeper zookeeper:2181
# delete topic
kafka-topics.sh --delete --zookeeper zookeeper:2181 --topic first_kafka_topic
# changing topic partitions
kafka-topics.sh --alter --zookeeper zookeeper:2181 --topic first_kafka_topic --partitions 2
kafka-topics.sh --alter --zookeeper zookeeper:2181 --topic first_kafka_topic --replication-factor 2
```

## Kafka Producer

```bash
kafka-console-producer.sh --broker-list kafka:9092 --topic first_kafka_topic
```

## Kafka Consumer

```bash
kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic first_kafka_topic
```

Consume from beginning

```bash
kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic first_kafka_topic --from-beginning
```

## Consumer Group

```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic first_kafka_topic --group my-first-application 
```

<!-- 
## Setting up kowl alongside

```
docker run -p 8080:8080 -e KAFKA_BROKERS=host.docker.internal:9092 quay.io/cloudhut/kowl:master
```
-->


# Theory

Apache Kafka is an open-source distributed event streaming platform that is designed for handling real-time data feeds and streams. It is used to process a continuous stream of information in real-time and pass it to stream processing systems.

Alternatives to Kafka are RabbitMQ, Google Pub / Sub, Redis Streams, Apache Flink and others.

## Basic Definitions

- Messages are grouped into categories called **topics**.
- The processes that publish messages into a topic are called **producers**.
- The processes that receive messages from a topic are called **consumers**.
- The processes or servers within Kafka that process messages are called **brokers**. The brokers in the Kafka cluster handle the process of receiving, storing and forwarding the messages to the consumers.

## Topic Structure

- A topic is divided into one or more partitions.
- A partition is also known as a **commit log**.
- Each partition contains an ordered set of messages.
- Each message is identified by its **offset** in the partition.
- Messages are added at one end of the partition and consumed at the other.

## Kafksa Consumer Offset

- The consumer offset is a way of tracking the sequential order in which messages are received by Kafka topics.
- The Kafka consumer offset allows processing to continue from where it last left off if the stream application is turned off or if there is an unexpected failure.
- Initially, when a Kafka consumer starts for a new topic, the offset begins at zero, but you might want to start from a later offset to avoid going through all messages from the beginning.

## Brokers and message processing

- Partitions allow messages in a topic to be distributted in multiple brokers, so that they can be processed in parallel.
- Each partition should fit in a single kafka server. It can also be replicated across several servers for fault-tolerance. One broker is marked as a leader for the partition and the others are marked as followers. If the leader fails, one of the followers automaticaly become the leader. (Zookeeper is used for the leader selection)
- Each machine in the cluster can run one broker.

## Pubsub

Kafka supports the publish-subscribe queue system.

- The system broadcasts the messages and the consumers subscribe to receive the messages. The difference with the queue system is that each message written on a partition sent to a consumer group, has to be consumed by only one consumer of this consumer group. 

## Why is kafka fast

- Kafka is optimized to maximize throughput i.e. moving a large volume of data efficiently.
- Sequential IO: Disk search is not necessarily faster than the memory access because everything depends on data access paterns. Access paterns can be random or sequential. 
- Sequential approach writes hundreds of MB per second while random writes hundreds of KB per second. By allowing Kafka to access large cheap hard disks sequentially data can be efficiently transferred.

## Outages

Let's say you have a service that consumes data from a topic, but unfortunately had an outage. How do you make sure it gets all messages written while being offline?

- **Consumer Group**: If you are using Kafka's consumer groups (which is a common practice for distributed consumer applications), Kafka will automatically track the offsets for each consumer in the group. When your consumer restarts, it will pick up from where it left off, consuming any messages that were produced during its downtime.
- **Manual Offset Management**: If you are not using consumer groups, you will need to manually manage the offsets. You can use Kafka's commit method to save the current offset, and then when the consumer restarts, you can seek to that offset to continue consuming.

## Consumer Groups

Messages are consumed by each consumer in a Kafka consumer group using a mechanism that ensures load balancing and fault tolerance. Here's how it works:

- **Partition Assignment**: Kafka topics are divided into partitions, and each partition is assigned to a single consumer within the group. This assignment is done automatically by Kafka.
- **Load Balancing**: When you have multiple consumers in a group, Kafka distributes the partitions of the topic evenly among the consumers. The goal is to balance the workload so that each consumer processes a roughly equal number of partitions and messages. Load balancing ensures that no one consumer is overwhelmed with too many partitions to handle.
- **Message Consumption**: Once the partitions are assigned to consumers, each consumer independently reads and processes messages from the partitions it's responsible for. This means that a message is processed by only one consumer within the group.
- **Committing Offsets**: As a consumer processes messages, it tracks the offsets of the messages it has consumed. It periodically commits these offsets back to Kafka. This is important for ensuring that, in case of a consumer failure or restart, the consumer can pick up from where it left off.
- **Rebalancing**: If a consumer in the group goes down or a new consumer joins the group, Kafka performs a rebalancing operation. During rebalancing, Kafka redistributes the partitions among the remaining consumers to maintain load balancing. Kafka tries to minimize disruption by ensuring that each partition is either assigned to an existing consumer or a newly added one. This process ensures fault tolerance and the continuity of message processing.
- **Offset Commit and Liveness**: To achieve at-least-once message processing semantics, it's important that offsets are committed only after the message has been successfully processed. This ensures that even in cases where a consumer crashes after processing but before committing the offset, the message won't be lost. Kafka allows you to control when offsets are committed, and you can commit offsets manually or automatically based on your application's requirements.

In summary, Kafka's consumer groups are designed to provide load balancing and fault tolerance for message consumption. Each message is processed by only one consumer within the group, and Kafka automatically handles the distribution of partitions and the recovery process in case of consumer failures or restarts. This makes Kafka a robust and scalable platform for processing large volumes of data across multiple consumers.

## Sources

- [Kafka Official Documentation](https://kafka.apache.org/documentation/#gettingStarted)
- [Kafka Video Sources](https://kafka.apache.org/videos)
- [Simplilearn](https://www.youtube.com/watch?v=U4y2R3v9tlY)
- [Intellipaat](https://www.youtube.com/watch?v=daRykH67_qs)
- [Kafka Consumer Offset](https://dattell.com/data-architecture-blog/understanding-kafka-consumer-offset/)
- [Kafka short intro](https://www.youtube.com/watch?v=UNUz1-msbOM)