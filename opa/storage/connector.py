from abc import ABC, abstractmethod
from typing import List, Dict
from kafka import KafkaProducer, KafkaConsumer
from opa.core.candlestick import Candlestick
from opa.utils import retry_connection_on_brokenpipe
from datetime import datetime
import pandas as pd
import happybase as hb



class InputOutputStream(ABC):

    @abstractmethod
    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        """
        Write list of Candlestick objects to the connector
        :param candlesticks: a list of Candlestick objects
        :param options: optional parameters
        :return:
        """
        pass

    @abstractmethod
    def write(self, candlestick: Candlestick, **options) -> None:
        """
        Write a single Candlestick object to  the connector.
        :param candlestick: a Candlestick object
        :param options: optional  parameters
        :return:
        """

    @abstractmethod
    def read(self, **options) -> List:
        pass


class CsvConnector(InputOutputStream):
    def write(self, candlestick: Candlestick, **options) -> None:
        pass

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        print(candlesticks)

    def read(self, list_files_csv: str, symbols: str, intervals: str) -> List:
        list_hbase_full = []
        for path_file in list_files_csv:
            print("Lecture du fichier: ", path_file)
            csv = pd.read_csv(path_file, delimiter=",", header=None)
            cols = [1, 2, 3, 4, 5, 6]
            data = csv[cols]

            data.insert(0, 'Symbols', symbols[0])
            data.insert(1, 'Intervals', intervals[0])

            data_rename = data.rename(
                columns={1: "Open", 2: "High", 3: "Low", 4: "Close", 5: "Volume", 6: "Close_Time"})
            data_clean = data_rename.values.tolist()
            for ligne in data_clean:
                inser = Candlestick(ligne[0], ligne[1], ligne[2], ligne[3], ligne[4], ligne[5], ligne[6], ligne[7])
                command_hbase = inser.to_hbase()
                list_hbase_full.append(command_hbase)

        return list_hbase_full


class HbaseTableConnector(InputOutputStream):

    def __init__(self, host="localhost", port=9090, table_name="BINANCE"):
        """
        Initialize Hbase client  and create table if not already exist
        """
        self.host = host
        self.port = port
        self.table_name = table_name
        self.pool = hb.ConnectionPool(size=3, host=self.host, port=self.port)
        self.__create_if_not_exist_table()

    @retry_connection_on_brokenpipe(5)
    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            with table.batch(**options) as b:
                for candlestick in candlesticks:
                    b.put(candlestick.key(), candlestick.to_hbase())

    def write(self, candlestick: Candlestick, **options) -> None:
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            try:
                table.put(candlestick.key(), candlestick.to_hbase())
            except IOError as e:
                print(f"{e}")
                pass

    def read(self,symbols:str,interval:str,date_start:int, date_stop:int) -> List:
        year_start = str(date_start)[0:4]
        month_start = str(date_start)[-2:]
        year_stop = str(date_stop)[0:4]
        month_stop = str(date_stop)[-2:]

        row_start = f'''{symbols}-{interval}#{year_start}{month_start}01'''
        row_stop = f'''{symbols}-{interval}#{year_stop}{month_stop}31'''
        datas = []
        keys = []
        symbols = []
        col_title = []
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            scan_data = table.scan(row_start=row_start, row_stop=row_stop)

        for key, data in scan_data:
            keys.append(key)
            datas.append(data)
        df_hbase = pd.DataFrame(datas, index=keys)
        df_hbase = df_hbase.apply(lambda x: x.apply(lambda y: float(y.decode("utf-8").replace('\'', ''))))
        for x in df_hbase:
            col_title.append(x)

        df_hbase['date'] = df_hbase[col_title[1]].apply(lambda x: datetime.fromtimestamp(x / 1000))
        return df_hbase

    def __create_if_not_exist_table(self) -> None:
        """
        Create table with Hbase client  if not exist.
        :return:
        """
        with self.pool.connection() as con:
            list_tables = con.tables()
            if self.table_name.encode("utf-8") not in list_tables:
                con.create_table(self.table_name, {'CANDLESTICKES': dict(), 'TECHNICAL_INDICATORS': dict()})


class KafkaConnector(InputOutputStream):

    ONE_CONS_TO_ALL_TOPICS: int = 1
    ONE_CONS_TO_ONE_TOPIC: int = 0

    def __init__(self,
                 bootstrapservers: str = "localhost:9092",
                 clientid: str = "opa_collector",
                 value_serializer=lambda v: v.encode("utf-8"),
                 value_deserializer=lambda v: v.decode("utf-8"),
                 api_version=(2, 8, 1)):
        self.bootstrap_servers = bootstrapservers
        self.client_id = clientid
        self.value_serializer = value_serializer
        self.value_deserializer = value_deserializer
        self.api_version = api_version

        self.kafka_producer = KafkaProducer(bootstrap_servers=bootstrapservers,
                                            client_id=clientid,
                                            value_serializer=value_serializer,
                                            api_version=api_version)

    def write_lines(self, candlesticks: List[Candlestick], **options) -> None:
        for candlestick in candlesticks:
            self.write(candlestick, **options)

    def write(self, candlestick: Candlestick, **options) -> None:
        self.kafka_producer.send(value=candlestick.__str__(), **options)
        self.kafka_producer.flush()

    def read(self, **options) -> Dict:
        topics = options.get("topics", [])
        mode = options.get("mode", self.ONE_CONS_TO_ALL_TOPICS)
        consumers = {}
        if mode == self.ONE_CONS_TO_ALL_TOPICS:
            key = "".join(str(topic) + "_" for topic in topics)
            consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers,
                                     client_id=self.client_id,
                                     value_deserializer=self.value_deserializer,
                                     auto_offset_reset='earliest')
            consumer.subscribe(topics)
            consumers[key] = consumer

        elif mode == self.ONE_CONS_TO_ONE_TOPIC:
            for topic_i in topics:
                consumers[topic_i] = KafkaConsumer(topics=topic_i,
                                                   bootstrap_servers=self.bootstrap_servers,
                                                   client_id=self.client_id,
                                                   value_deserializer=self.value_deserializer,
                                                   auto_offset_reset='earliest')
        else:
            raise ValueError("Bad mode argument")

        return consumers
