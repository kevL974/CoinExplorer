from pyspark.sql import functions as F
from pyspark.sql.window import Window

def calculate_moving_average(df, n: int):
    # Je vérifie si la colonne "CANDLESTICK:close" existe dans mon DataFrame
    if "CANDLESTICK:close" not in df.columns:
        raise ValueError("La colonne 'CANDLESTICK:close' n'existe pas dans mon DataFrame.")
    
    # Je crée une fenêtre pour le calcul de la moyenne mobile
    window_spec = Window.orderBy("timestamp").rowsBetween(-n+1, Window.currentRow)
    
    # J'ajoute une colonne avec la moyenne mobile calculée sur n périodes
    df_with_ma = df.withColumn(f"MA-{n}", F.avg("CANDLESTICK:close").over(window_spec))
    
    return df_with_ma

# exemple d'utilisation

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("TestMovingAverage") \
    .getOrCreate()
data = [("2023-01-01", 10),
        ("2023-01-02", 15),
        ("2023-01-03", 20),
        
       ]

columns = ["timestamp", "CANDLESTICK:close"]

df = spark.createDataFrame(data, columns)


# output: print(df)  DataFrame[timestamp: string, CANDLESTICK:close: bigint]

n = 3  # pour trois périodes
df_with_ma = calculate_moving_average(df, n)

df_with_ma.show()

# output
#+----------+-----------------+----+
#| timestamp|CANDLESTICK:close|MA-3|
#+----------+-----------------+----+
#|2023-01-01|               10|10.0|
#|2023-01-02|               15|12.5|
#|2023-01-03|               20|15.0|
#+----------+-----------------+----+
