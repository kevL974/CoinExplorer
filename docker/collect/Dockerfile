FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY requirements.txt .

RUN apk update && apk add build-base && pip3 install --no-cache-dir -r requirements.txt

ADD opa ./opa

ENTRYPOINT ["python3", "-um", "opa.harvest.collect", "-d", "hbase:9090", "-k", "kafka:9092"]

CMD ["-s", "ETHUSDT","-i","1m","15m"]