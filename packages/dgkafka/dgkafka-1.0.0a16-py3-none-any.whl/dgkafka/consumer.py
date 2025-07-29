from typing import Literal, Iterator, Any
from dgkafka.errors import ConsumerNotSetError

from confluent_kafka import Consumer, KafkaException, Message, TopicPartition
from confluent_kafka import OFFSET_STORED, OFFSET_BEGINNING, OFFSET_END

import logging
import dglog

OffsetType = Literal[OFFSET_STORED, OFFSET_BEGINNING, OFFSET_END] | int


class KafkaConsumer:
    def __init__(self, logger_: logging.Logger | dglog.Logger | None = None, **configs: Any) -> None:
        self.consumer: Consumer | None = None
        self.logger = logger_ if logger_ else dglog.Logger()
        if isinstance(self.logger, dglog.Logger):
            self.logger.auto_configure()
        self._init_consumer(**configs)

    def _init_consumer(self, **configs: Any) -> None:
        """Internal method to initialize consumer"""
        try:
            self.consumer = Consumer(configs)
            self.logger.info("[*] Consumer initialized successfully")
        except KafkaException as ex:
            self.logger.error(f"[x] Failed to initialize consumer: {ex}")
            raise

    def close(self) -> None:
        """Safely close the consumer"""
        if self.consumer is not None:
            try:
                self.consumer.close()
                self.logger.info("[*] Consumer closed successfully")
            except KafkaException as ex:
                self.logger.error(f"[x] Error closing consumer: {ex}")
                raise
            finally:
                self.consumer = None

    def __enter__(self):
        """Context manager entry point"""
        if self.consumer is None:
            self._init_consumer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        self.close()

    def _ensure_consumer(self) -> Consumer:
        """Ensure consumer is initialized"""
        if self.consumer is None:
            raise ConsumerNotSetError('[!] Consumer not initialized!')
        return self.consumer

    def subscribe(self, topics: str | list[str], partition: int | None = None,
                  offset: OffsetType = OFFSET_STORED) -> None:
        """Subscribe to topics"""
        consumer = self._ensure_consumer()

        if partition is not None and offset != OFFSET_STORED:
            topic_list = [topics] if isinstance(topics, str) else topics
            for topic in topic_list:
                self._assign_topic_partition(topic, partition, offset)
        else:
            topics_list = [topics] if isinstance(topics, str) else topics
            consumer.subscribe(topics_list)
            self.log_subscription_info()
            # self.logger.info(f"[*] Subscribed to topics: {topics_list}")

    def _assign_topic_partition(self, topic: str, partition: int, offset: OffsetType) -> None:
        """Assign to specific partition"""
        consumer = self._ensure_consumer()
        topic_partition = TopicPartition(topic, partition, offset)
        consumer.assign([topic_partition])
        consumer.seek(topic_partition)
        self.logger.info(f"[*] Assigned to topic '{topic}' partition {partition} with offset {offset}")

    def consume(self, num_messages: int = 1, timeout: float = 1.0, decode_: bool = False) -> Iterator[Message | str]:
        """Consume messages"""
        consumer = self._ensure_consumer()

        for _ in range(num_messages):
            if (msg := self._consume(consumer, timeout)) is None:
                continue
            yield msg.value().decode('utf-8') if decode_ else msg

    def _consume(self, consumer: Consumer, timeout: float) -> Message | None:
        msg = consumer.poll(timeout)
        if msg is None:
            return None
        if msg.error():
            self.logger.error(f"[x] Consumer error: {msg.error()}")
            return None
        self.logger.info(f"[<] Received message from {msg.topic()} [partition {msg.partition()}, offset {msg.offset()}]")
        self.logger.debug(f"[*] Message content: {msg.value()}")
        return msg

    def commit(self, message: Message | None = None, offsets: list[TopicPartition] | None = None,
               asynchronous: bool = True) -> list[TopicPartition] | None:
        """Commit offsets to Kafka."""
        consumer = self._ensure_consumer()
        if message:
            return consumer.commit(message=message, asynchronous=asynchronous)
        elif offsets:
            return consumer.commit(offsets=offsets, asynchronous=asynchronous)
        return consumer.commit(asynchronous=asynchronous)

    def get_subscription_info(self) -> dict:
        """Get current subscription and assignment information.

        Returns:
            dict: Dictionary with subscription and assignment details
            {
                'subscribed_topics': list[str] | None,
                'assignments': list[dict] | None,
                'current_offsets': list[dict] | None
            }
        """
        consumer = self._ensure_consumer()

        try:
            # Получаем текущие подписки
            subscribed_topics = consumer.subscription()

            # Получаем текущие назначения (assignments)
            assignments = consumer.assignment()

            # Получаем текущие позиции (offsets)
            current_offsets = []
            if assignments:
                current_offsets = consumer.position(assignments)

            # Формируем информацию о назначениях
            assignments_info = []
            for tp in assignments:
                assignments_info.append({
                    'topic': tp.topic,
                    'partition': tp.partition,
                    'offset': tp.offset
                })

            # Формируем информацию о текущих позициях
            offsets_info = []
            for tp in current_offsets:
                offsets_info.append({
                    'topic': tp.topic,
                    'partition': tp.partition,
                    'offset': tp.offset
                })

            return {
                'subscribed_topics': list(subscribed_topics) if subscribed_topics else None,
                'assignments': assignments_info if assignments_info else None,
                'current_offsets': offsets_info if offsets_info else None
            }
        except KafkaException as ex:
            self.logger.error(f"[x] Failed to get subscription info: {ex}")
            raise

    def log_subscription_info(self) -> None:
        """Log current subscription and assignment information."""
        info = self.get_subscription_info()

        if info['subscribed_topics']:
            self.logger.info(f"[*] Subscribed topics: {', '.join(info['subscribed_topics'])}")
        else:
            self.logger.info("[!] Not subscribed to any topics")

        if info['assignments']:
            self.logger.info("[*] Current assignments:")
            for assignment in info['assignments']:
                self.logger.info(f"    - {assignment['topic']} [partition {assignment['partition']}]")
        else:
            self.logger.info("[!] No partition assignments")

        if info['current_offsets']:
            self.logger.info("[*] Current offsets:")
            for offset in info['current_offsets']:
                self.logger.info(f"    - {offset['topic']} [partition {offset['partition']}]: offset {offset['offset']}")
