#!/bin/bash

wget https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz \
&& sudo tar -xzf ta-lib-0.6.4-src.tar.gz \
&& sudo rm ta-lib-0.6.4-src.tar.gz \
&& cd ta-lib-0.6.4/ \
&& sudo ./configure --prefix=/usr \
&& sudo make \
&& sudo make install \
&& cd .. \
&& sudo rm -rf ta-lib-0.6.4/ \
&& pip install ta-lib --break-system-packages
