FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

ARG API_KEY
ARG API_SECRET

ENV API_KEY_BINANCE_TESTNET=$API_KEY
ENV API_KEY_SECRET_BINANCE_TESTNET=$API_SECRET

RUN echo ${API_KEY_BINANCE_TESTNET}
WORKDIR /app

COPY requirements.txt .

RUN apk update && apk add build-base && pip3 install --no-cache-dir -r requirements.txt

ADD opa ./opa

ADD collect_stream_data .

ENTRYPOINT ["python3", "binance_stream_data_collector.py", "-k", "kafka:9092"]

CMD ["-s", "ETHUSDT","-i", "1m", "15m"]
