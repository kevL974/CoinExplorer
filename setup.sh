#!/bin/bash

docker image build \
--tag opa_collect:latest \
--build-arg api_key=${API_KEY_BINANCE_TESTNET} \
--build-arg api_secret=${API_KEY_SECRET_BINANCE_TESTNET} \
--file docker/collect/Dockerfile . && \

docker image build \
--tag opa_streaming:latest \
--file docker/streaming/Dockerfile . && \

docker image build \
--tag opa_hbase:latest \
--file docker/hbase/Dockerfile . && \

docker volume prune -f && docker-compose -f docker/docker-compose.yml up --scale kafka=3 -d