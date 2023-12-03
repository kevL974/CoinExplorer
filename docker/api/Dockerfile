FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

WORKDIR /app

COPY requirements.txt .

RUN apk update && apk add build-base && pip3 install --no-cache-dir -r requirements.txt

ADD opa ./opa
WORKDIR /app/opa/api

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]