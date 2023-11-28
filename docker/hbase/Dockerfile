
FROM openjdk:8-jdk

ENV HBASE_VERSION 2.5.5
ENV HBASE_HOME /opt/hbase

RUN apt-get update  &&  apt-get  install -y netcat
RUN wget https://dlcdn.apache.org/hbase/stable/hbase-${HBASE_VERSION}-bin.tar.gz && \
    tar -xvf hbase-${HBASE_VERSION}-bin.tar.gz -C /opt/ && \
    mv /opt/hbase-${HBASE_VERSION} ${HBASE_HOME} && \
    rm hbase-${HBASE_VERSION}-bin.tar.gz

COPY docker/hbase/hbase-site.xml ${HBASE_HOME}/conf/

EXPOSE 16000 16010 16020 16030 9090

ENTRYPOINT ["/bin/bash", "-c", "${HBASE_HOME}/bin/start-hbase.sh && ${HBASE_HOME}/bin/hbase-daemon.sh start thrift && tail -f /dev/null" ]
