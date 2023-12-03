from fastapi import FastAPI, Query
from typing import Annotated
import pandas as pd
import happybase as hb
import os
import uvicorn
from datetime import datetime

app = FastAPI(title="OPA the cryptocurrency genius",
              description="I'm OPA the cryptocurrency genius, make a request and i will grant it...")

#hbase_host = os.getenv("DATABASE_HOST")
#hbase_port = os.getenv("DATABASE_PORT")
hbase_host = '127.0.0.1'
hbase_port = 9090
pool = hb.ConnectionPool(size=3, host=hbase_host, port=hbase_port)
TABLE_BINANCE = 'BINANCE'

@app.get('/')
def get_index():
    return {'genius': 'Hi everyone, please make your request... '}


@app.get("/health", name="Check if API works")
def health_check():
    """
    Check if API works
    """
    return {"status": "ok"}


@app.get("/candlesticks", name="Get candlesticks data of symbols")
def get_candelsticks(symbol: str, interval: str, start: str, end: str):
    """
    Returns candlesticks data according to this request parameters.
    :param symbol: the name of crypto asset (choices : ['BTCUSDT, ETHUSDT']).
    :param interval: candlesticks interval.
    :param start: starting date of candlesticks.
    :param end: endind date of candlesticks.
    :return: List of candlesticks in json format
    """
    return get_candlesticks_from_database(symbol,interval,start,end)


def get_candlesticks_from_database(symbols:str,interval:str,date_start:str, date_stop:str):
    row_start = f'''{symbols}-{interval}#{date_start}'''
    row_stop = f'''{symbols}-{interval}#{date_stop}'''

    with pool.connection() as con:
        table = con.table(TABLE_BINANCE)
        candlesticks = [data for key, data in table.scan(row_start=row_start,row_stop=row_stop)]

    df = pd.DataFrame(candlesticks).apply(lambda x: x.apply(lambda y: float(y.decode("utf-8").replace('\'', ''))))
    columns = [c.decode("utf-8") for c in df.columns]
    df.columns = columns
    df['CANDLESTICKES:close_time'] = df['CANDLESTICKES:close_time'].apply(lambda x: int(x))
    df['date'] = df['CANDLESTICKES:close_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
    df.set_index('date',inplace=True)

    return df.to_json(orient='index')


if __name__ == "__main__":
    uvicorn.run("server_api:app", port=80, reload=True)