FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY requirements.txt .

RUN apk update && apk add build-base && pip3 install --no-cache-dir -r requirements.txt

ADD opa ./opa

ADD stream_to_hbase .

ENTRYPOINT ["python3", "-um", "stream_to_hbase.py", "-d", "hbase:9090", "-k", "kafka:9092"]

CMD ["-s", "BTCUSDT",  "ETHUSDT"]