FROM python:3.10-slim
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY pyproject.toml .

COPY src/opa ./opa

RUN apt-get update && apt-get install -y build-essential && pip install '.[api]'

COPY services/api .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]