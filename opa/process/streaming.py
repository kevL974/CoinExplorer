from kafka import KafkaConsumer
import happybase
import json


if __name__ == "__main__":


    # Configuration de Kafka
    consumer = KafkaConsumer(
        'BTCUSDT',
        bootstrap_servers='localhost:9092',
        group_id='mygroup',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    # Connexion à HBase
    connection = happybase.Connection('localhost')
    table = connection.table('binance')

    try:
        for message in consumer:
            data = message.value
            table.put(data['id'], data)

    except KeyboardInterrupt:
        pass
    finally:
        # Fermeture de la connexion à HBase
        connection.close()