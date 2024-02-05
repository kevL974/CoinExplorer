#!/bin/bash

docker image build \
--tag opa_collect_historic_data:latest \
--build-arg api_key=${API_KEY_BINANCE_TESTNET} \
--build-arg api_secret=${API_KEY_SECRET_BINANCE_TESTNET} \
--file docker/collect_historic_data/Dockerfile . && \

docker image build \
--tag opa_streaming:latest \
--file docker/streaming/Dockerfile . && \

docker image build \
--tag opa_hbase:latest \
--file docker/hbase/Dockerfile . && \

docker image build \
--tag opa_api:latest \
--file docker/api/Dockerfile . && \

docker image build \
--tag opa_dashboard:latest \
--file docker/dashboard/Dockerfile . && \

docker volume prune -f && docker-compose -f docker/docker-compose.yml up --scale kafka=3 -d