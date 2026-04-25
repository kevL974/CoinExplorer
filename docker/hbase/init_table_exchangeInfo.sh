#!/bin/bash

# Nom de la table
table_name="INFO"

# Noms des familles de colonnes
column_family1="MARKETDATA"

# Vérifier si la table existe déjà
table_exists=$(echo "list '$table_name'" | hbase shell | grep -o "$table_name")

if [ -z "$table_exists" ]; then
    # Si la table n'existe pas, la créer
    echo "create '$table_name', '$column_family1', '$column_family2'" | hbase shell
    echo "Table $table_name créée avec succès."
else
    # Si la table existe déjà, afficher un message
    echo "La table $table_name existe déjà."
fi