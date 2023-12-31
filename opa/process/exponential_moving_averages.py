from pyspark.sql import functions as F
from pyspark.sql.window import Window

def calculate_ema(df, n):
    close_column = "CANDLESTICK:close"
    
    if close_column not in df.columns:
        raise ValueError(f"La colonne '{close_column}' n'existe pas dans mon DataFrame.")

    alpha = 2 / (n + 1)

    window_spec = Window.orderBy("timestamp")

    df_with_ema = df.withColumn("lag_value", F.lag(close_column).over(window_spec)) \
                    .withColumn("EMA-{}".format(n), F.coalesce((1 - alpha) * F.col("lag_value") + alpha * F.col(close_column), F.col(close_column))) \
                    .drop("lag_value")
    
    return df_with_ema


# Exemple 
# Création de la session Spark
spark = SparkSession.builder.appName("TestEMA").getOrCreate()

# Création du DataFrame
data = [("2023-01-01", 10),
        ("2023-01-02", 15),
        ("2023-01-03", 20),
       ]

columns = ["timestamp", "CANDLESTICK:close"]

df = spark.createDataFrame(data, columns)


n = 3
df_with_ema = calculate_ema(df, n)

# Afficher le résultat
df_with_ema.show()


#+----------+-----------------+-----+
#| timestamp|CANDLESTICK:close|EMA-3|
#+----------+-----------------+-----+
#|2023-01-01|               10| 10.0|
#|2023-01-02|               15| 12.5|
#|2023-01-03|               20| 17.5|
#+----------+-----------------+-----+
