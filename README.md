# SEPT23-BDE-OPA

# I - Description
OPA a pour objectif de permettre aux utilisateurs d’analyser les actifs numériques (Bitcoin, Etherum, Altcoin, etc)  mis à disposition de la plateforme Binance et de pouvoir comparer les performances (rentabilité, précision, etc) des modèles de machine learning spécialisées dans la décision d’achat et de vente de cryptomonnaie.


# II - Pour commencer
## A - Démarrer  l'environnement
Exécutez le  script  `setup.sh` pour lancer l'environnement complet de la solution OPA qui comprend plusieurs services :
- **zookeeper** -> l'orchestrateur de ressources de kafka
- **kafka** -> une plateforme distribuée de diffusion de données en continue, avec 2 topics par défaut BTCUSDT et ETHUSDT
- **hbase** -> une base de données orientée colonnes, qui contient une table "BINANCE" avec les données de type bougies financières (candlestick) et des indicateurs statistiques
- **collect** -> un container qui fait tourner le script collect.py chargé de collecter les données historiques et temps réel sur la plateforme binance
## B - Utiliser les données via un notebook
- Dans un terminal, executer la commande suivante `docker logs docker_jupyter_1`,  la  commande  retournera  une url; 
- Copier l'URL dans le navigateur pour avoir accès un jupyterLab.
# III - Aspect du projet