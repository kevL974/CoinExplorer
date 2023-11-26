FROM python:3.10-bullseye
LABEL authors="kevin"

ARG api_key
ARG api_secret

ENV API_KEY_BINANCE_TESTNET $api_key
ENV API_KEY_SECRET_BINANCE_TESTNET $api_secret
# Définissez un répertoire de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers de dépendances dans le répertoire de travail
COPY requirements.txt .

# Installez les dépendances
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiez le code source dans le répertoire de travail
ADD opa ./opa

ENTRYPOINT ["python3", "-um", "opa.harvest.collect", "-d", "hbase:9090", "-k", "kafka:9092"]
# Exécutez l'application
CMD ["-s", "ETHUSDT", "-i", "15m"]