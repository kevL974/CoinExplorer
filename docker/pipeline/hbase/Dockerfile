FROM python:3.10-slim
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY pyproject.toml .

COPY src/opa ./opa

RUN apt-get update && apt-get install -y build-essential && pip install '.'

COPY services/pipeline/hbase .

ENTRYPOINT ["python3", "-um", "stream_to_hbase.py", "-d", "hbase:9090", "-k", "kafka:9092"]

CMD ["-s", "BTCUSDT",  "ETHUSDT"]