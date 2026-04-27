FROM python:3.10-slim
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY pyproject.toml .

COPY src/opa ./src/opa

RUN apt-get update && apt-get install -y build-essential && pip install '.[dashboard]'

EXPOSE 5000

CMD ["python3", "dashboard.py"]