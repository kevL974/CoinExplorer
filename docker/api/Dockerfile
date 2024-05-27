FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

WORKDIR /app

ADD api .

RUN apk update && apk add build-base && pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

expose 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]