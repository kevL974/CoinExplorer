# Utiliser une image de base avec Java 8 (HBase a besoin de Java)
FROM openjdk:8-jdk

# Définir les variables d'environnement pour HBase
ENV HBASE_VERSION 2.5.5
ENV HBASE_HOME /opt/hbase

RUN apt-get update  &&  apt-get  install -y netcat
# Télécharger HBase et l'installer
RUN wget https://dlcdn.apache.org/hbase/stable/hbase-${HBASE_VERSION}-bin.tar.gz && \
    tar -xvf hbase-${HBASE_VERSION}-bin.tar.gz -C /opt/ && \
    mv /opt/hbase-${HBASE_VERSION} ${HBASE_HOME} && \
    rm hbase-${HBASE_VERSION}-bin.tar.gz

# Ajouter le fichier de configuration HBase
COPY docker/hbase/hbase-site.xml ${HBASE_HOME}/conf/

# Exposer les ports nécessaires
EXPOSE 16000 16010 16020 16030 9090

# Définir le point d'entrée pour démarrer HBase en mode autonome et le serveur Thrift
ENTRYPOINT ["/bin/bash", "-c", "${HBASE_HOME}/bin/start-hbase.sh && ${HBASE_HOME}/bin/hbase-daemon.sh start thrift && tail -f /dev/null" ]
