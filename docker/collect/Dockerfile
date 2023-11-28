FROM python:3.10-bullseye
LABEL authors="kevin"

ARG api_key
ARG api_secret

ENV API_KEY_BINANCE_TESTNET $api_key
ENV API_KEY_SECRET_BINANCE_TESTNET $api_secret

WORKDIR /app

COPY requirements.txt .


RUN pip3 install --no-cache-dir -r requirements.txt

ADD opa ./opa

ENTRYPOINT ["python3", "-um", "opa.harvest.collect", "-d", "hbase:9090", "-k", "kafka:9092"]

CMD ["-s", "ETHUSDT", "-i", "15m"]