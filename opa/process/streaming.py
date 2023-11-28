import asyncio
from kafka import KafkaConsumer
from opa.storage.connector import KafkaConnector, HbaseTableConnector, InputOutputStream
from opa.utils import *
import argparse
import json


def message_consummable(consumer: KafkaConsumer):
    try:
        for message in consumer:
            yield message
    except KeyboardInterrupt:
        consumer.close()


async def store_to_database(consumer: KafkaConsumer, output: InputOutputStream, lock: asyncio.Lock) -> None:
    """
    Consumes data from Kafka topic and sends it to ouput.
    :param consumer: a Kafka consumer
    :param output: InputOutputStream object, can be HBaseTableConnector for exemple.
    :param lock: a asyncio.Lock object
    :return:
    """

    for msg in message_consummable(consumer):
        print(msg.value)
        candlestick = dict_to_candlesticks(json.loads(msg.value))
        async with lock:
            output.write(candlestick)


async def process_stream_data(consumers: Dict[str, KafkaConsumer], output: InputOutputStream) -> None:
    stream_processors = []
    lock = asyncio.Lock()
    for topic_i, consumer_i in consumers.items():
        stream_processors.append(asyncio.ensure_future(store_to_database(consumer_i, output, lock)))

    finished, _ = await asyncio.wait(stream_processors)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Launch streaming process')
    parser.add_argument('-t', '--topics',
                        help='list of topics as input stream  : -t  <topic1>,<topics2>',
                        nargs='+',
                        type=str,
                        required=True)
    parser.add_argument('-k', '--kafka',
                        help='kafka connection setting : -k <ip_boostrapserver>:<port_bootstrapserver>',
                        type=str,
                        required=True)
    parser.add_argument('-d', '--database',
                        help='database connection setting : -d <ip_database>:<port_database>',
                        type=str,
                        required=True)
    parser.add_argument('--debug', help='activate debug mode', action='store_true')
    args = parser.parse_args()

    topics = args.topics
    kafka_host, kafka_port = parse_connection_settings(args.kafka)
    db_host, db_port = parse_connection_settings(args.database)

    input_kafka = KafkaConnector(bootstrapservers=args.kafka, clientid="opa_consumor")
    output_hbase = HbaseTableConnector(host=db_host, port=db_port)

    kafka_consumers = input_kafka.read(topics=topics, mode=KafkaConnector.ONE_CONS_TO_ALL_TOPICS)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_stream_data(kafka_consumers, output_hbase))
