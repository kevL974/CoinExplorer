FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY requirements.txt .

RUN apk update && apk add build-base && pip3 install --no-cache-dir -r requirements.txt

ADD opa ./opa

ADD collect_historic_data .

ENTRYPOINT ["python3", "binance_historic_data_collector.py", "-d", "hbase:9090"]

CMD ["-s", "ETHUSDT","-i", "1m", "15m"]
