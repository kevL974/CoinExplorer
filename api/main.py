from fastapi import FastAPI, HTTPException
from typing import Optional, List, Tuple
from datetime import datetime
import pandas as pd
import happybase as hb
import uvicorn
import os

app = FastAPI(title="OPA the cryptocurrency genius",
              description="I'm OPA the cryptocurrency genius, make a request and i will grant it...")

hbase_host = os.getenv("DATABASE_HOST")
hbase_port = int(os.getenv("DATABASE_PORT"))

pool = hb.ConnectionPool(size=3, host=hbase_host, port=hbase_port)
TABLE_BINANCE = 'BINANCE'
TABLE_INFO = 'INFO'
COLUMNS = ['CANDLESTICKES:close', 'CANDLESTICKES:close_time', 'CANDLESTICKES:high',
       'CANDLESTICKES:low', 'CANDLESTICKES:open', 'CANDLESTICKES:volume']


@app.get('/')
def get_index():
    return {'genius': 'Hi everyone, please make your request... '}


@app.get("/status", name="Check if API works")
def health_check():
    """
    Check if API works, returns 1 if it lives, 0 else
    """
    return {"status": 1}


@app.get("/candlesticks", name="Get candlesticks")
def get_candelsticks(symbol: str, interval: str, start: str, end: str):
    """
    Returns candlesticks data according to this request parameters.
    :param symbol: the name of crypto asset (choices : ['BTCUSDT, ETHUSDT']).
    :param interval: candlesticks interval.
    :param start: starting date of candlesticks. Example : start=20220101 or start=20230217.
    :param end: endind date of candlesticks. Example : end=20211105 or end=20230822.
    :return: List of candlesticks in json format
    """
    valid_start, valid_end = is_valid_date_params(start, end)

    candlesticks = get_candlesticks_over_a_period(symbol, interval, valid_start, valid_end)

    return to_json_format(candlesticks)


@app.get("/assets", name="Get available digital assets")
def get_digital_assets():
    """
    Returns digital assets available on server.
    :return: List of digital assets in json format
    """
    with pool.connection() as con:
        table = con.table(TABLE_INFO)
        keys = [key for key, data in table.scan()]
    return keys


def get_candlesticks_over_a_period(symbol: str, interval: str, start: str, end: str) -> List:
    row_start = f"{symbol}-{interval}#{start}"
    row_stop = f"{symbol}-{interval}#{end}"

    with pool.connection() as con:
        table = con.table(TABLE_BINANCE)
        candlesticks = [data for key, data in table.scan(row_start=row_start.encode("utf-8"),
                                                         row_stop=row_stop.encode("utf-8"))]

    return candlesticks


def to_json_format(candlesticks: List) -> str:
    """
    Transforms list of candlesticks data to a json document.
    :param candlesticks: list of candlesticks data
    :return: a json document.
    """
    if not candlesticks:
        df = pd.DataFrame(data=[], columns=COLUMNS)
    else:
        df = pd.DataFrame(candlesticks).apply(lambda x: x.apply(lambda y: float(y.decode("utf-8").replace('\'', ''))))
        columns = [c.decode("utf-8") for c in df.columns]
        df.columns = columns
        df['CANDLESTICKES:close_time'] = df['CANDLESTICKES:close_time'].apply(lambda x: int(x))
        df['date'] = df['CANDLESTICKES:close_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        df.set_index('date', inplace=True)

    return df.to_json(orient='index')


def is_date_before_today(date: datetime) -> bool:
    """
    Checks if date is earlier than today.
    :param date: a datetime object
    :return: True if date is earlier than today, else False.
    """
    today = datetime.now()
    return today >= date


def str_to_datetime(date: str) -> datetime:
    """
    Transforms date string (YYYYMMDD) to datetime object.
    :param date: a date string.
    :return: a datetime object.
    """
    try:
        return datetime.strptime(date, "%Y%m%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Bad date format")


def is_valid_date_params(start: str, end: str) -> Tuple[str, str]:
    """
    Checks if date params are in good format, then if start date and end date are before today's date.
    :param start: start date.
    :param end: end date.
    :return: a Tuple with valid start date and end date.
    """
    date_start = str_to_datetime(start)
    if not is_date_before_today(date_start):
        raise HTTPException(status_code=422,
                            detail=f"Invalid date value, it should be before today but "
                                   f"start({start}) > today({datetime.now().strftime('%Y%m%d')})")

    date_end = str_to_datetime(end)
    if not is_date_before_today(date_end):
        raise HTTPException(status_code=422,
                            detail=f"Invalid date value, it should be before today but "
                                   f"end({end}) > today({datetime.now().strftime('%Y%m%d')})")

    if date_start > date_end:
        tmp = start
        start = end
        end = tmp
        return start, end

    return start, end


if __name__ == "__main__":
    uvicorn.run("main:app", port=5051, reload=True)