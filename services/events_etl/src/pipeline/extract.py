from kafka import KafkaConsumer

def extract_batch(
        consumer: KafkaConsumer,
        topic: str,
        start_timestamptz: str,
        stop_timestamptz: str,
        ):
    partitions = consumer.partitions_for_topic(topic)
    print(partitions)
    # if partitions is None:
    #     print(f"Skipping topic {topic}: no partitions")
    #     return [], start_timestamp

    # topic_partitions = [TopicPartition(topic, p) for p in partitions]
    # timestamps = {tp: start_timestamp for tp in topic_partitions}
    # offsets = consumer.offsets_for_times(timestamps)

    # for tp, offset_data in offsets.items():
    #     if offset_data is not None:
    #         consumer.assign([tp])
    #         consumer.seek(tp, offset_data.offset)
    #     else:
    #         # No offset found for timestamp, start from earliest
    #         consumer.assign([tp])
    #         consumer.seek_to_beginning(tp)

    # batch = []
    # max_timestamp = start_timestamp

    # while len(batch) < BATCH_SIZE:
    #     raw_msgs = consumer.poll(timeout_ms=1000)
    #     if not raw_msgs:
    #         break
    #     for tp, messages in raw_msgs.items():
    #         for msg in messages:
    #             batch.append(msg.value)
    #             max_timestamp = max(max_timestamp, msg.timestamp)

    # return batch, max_timestamp