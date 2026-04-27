FROM python:3.10-slim
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY pyproject.toml .

COPY src/opa ./src/opa

RUN apt-get update && apt-get install -y build-essential && pip install '.'

COPY services/collectors/stream .

ENTRYPOINT ["python3", "binance_stream_data_collector.py", "-k", "kafka:9092"]

CMD ["-s", "ETHUSDT","-i", "1m", "15m"]
