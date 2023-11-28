from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql import SparkSession


def calculate_moving_average(df, n: int):
    if "CANDLESTICK:close" not in df.columns:
        raise ValueError("La colonne 'CANDLESTICK:close' n'existe pas dans mon DataFrame.")

    window_spec = Window.orderBy("timestamp").rowsBetween(-n+1, Window.currentRow)

    df_with_ma = df.withColumn(f"MA-{n}", F.avg("CANDLESTICK:close").over(window_spec))
    
    return df_with_ma

spark = SparkSession.builder \
    .appName("TestMovingAverage") \
    .getOrCreate()
data = [("2023-01-01", 10),
        ("2023-01-02", 15),
        ("2023-01-03", 20),
       ]

columns = ["timestamp", "CANDLESTICK:close"]

df = spark.createDataFrame(data, columns)

n = 3
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
