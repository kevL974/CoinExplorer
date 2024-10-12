from opa.trading.technic.strategy import *
from opa.trading.technic.technical_analysis import *
from opa.core.candlestick import Candlestick
from opa.utils import parse_connection_settings, dict_to_candlesticks
from opa.storage.connector import KafkaConnector
from kafka import KafkaConsumer
import argparse
import asyncio
import json


class TradingBot:

    def __init__(self, strategy: TradingStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> TradingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: TradingStrategy) -> None:
        self._strategy = strategy

    def submit_new_candlestick(self, candlestick: Candlestick) -> None:
        self._strategy.indicators.current_candlestick = candlestick
        self._strategy.indicators.notify()


async def run_bot(consumer: KafkaConsumer, bot: TradingBot) -> None:
    for msg in consumer:
        candlestick = dict_to_candlesticks(json.loads(msg.value))
        bot.submit_new_candlestick(candlestick)


async def trade(consumers: Dict[str, KafkaConsumer], bot: TradingBot) -> None:
    processors = []
    for topic_i, consumer_i in consumers.items():
        processors.append(asyncio.ensure_future(run_bot(consumer=consumer_i, bot=bot)))
    finished, _ = await asyncio.wait(processors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start trading with a bot')
    parser.add_argument('-t', '--topic',
                        help='Topic where are price data : -t  <topic>',
                        type=str,
                        required=True)
    parser.add_argument('-k', '--kafka',
                        help='kafka connection setting : -k <ip_boostrapserver>:<port_bootstrapserver>',
                        type=str,
                        required=True)

    parser.add_argument('--backtest', help='Backtesting mode', action='store_true')

    args = parser.parse_args()

    topic = args.topic
    kafka_host, kafka_port = parse_connection_settings(args.kafka)

    input_kafka = KafkaConnector(bootstrapservers=args.kafka, clientid="opa_bot_consumor")
    kafka_consumers = input_kafka.read(topics=topic, mode=KafkaConnector.ONE_CONS_TO_ALL_TOPICS)

    bot = TradingBot(SwingTradingStrategy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(trade(consumers=kafka_consumers, bot=bot))
