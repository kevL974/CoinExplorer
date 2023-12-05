FROM python:3.10-alpine
LABEL authors="OPA_Datascientest"

WORKDIR /app

ADD dashboard .

RUN apk update && apk add build-base && pip3 install --no-cache-dir -r requirements.txt

expose 5000

CMD ["python3", "dashboard.py"]