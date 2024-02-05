FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY requirements.txt .

RUN apk update && apk add build-base && pip3 install --no-cache-dir -r requirements.txt

ADD opa ./opa

ADD collect .

ENTRYPOINT ["python3", "binance_collector.py", "-d", "hbase:9090", "-k", "kafka:9092"]

CMD ["-s", "ETHUSDT","-i","1d", "--skip_stream_data"]
