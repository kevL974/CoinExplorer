from fastapi import FastAPI, HTTPException
from typing import Optional, List, Tuple
from datetime import datetime
import pandas as pd
import happybase as hb
import uvicorn

app = FastAPI(title="OPA the cryptocurrency genius",
              description="I'm OPA the cryptocurrency ls -algenius, make a request and i will grant it...")

#hbase_host = os.getenv("DATABASE_HOST")
#hbase_port = os.getenv("DATABASE_PORT")
hbase_host = '127.0.0.1'
hbase_port = 9090
pool = hb.ConnectionPool(size=3, host=hbase_host, port=hbase_port)
TABLE_BINANCE = 'BINANCE'


@app.get('/')
def get_index():
    return {'genius': 'Hi everyone, please make your request... '}


@app.get("/status", name="Check if API works")
def health_check():
    """
    Check if API works, returns 1 if it lives, 0 else
    """
    return {"status": 1}


@app.get("/candlesticks", name="Get candlesticks data of symbols")
def get_candelsticks(symbol: str, interval: str, start: str, end: Optional[str]):
    """
    Returns candlesticks data according to this request parameters.
    :param symbol: the name of crypto asset (choices : ['BTCUSDT, ETHUSDT']).
    :param interval: candlesticks interval.
    :param start: starting date of candlesticks. Example : start=202201 or start=20230217.
    :param end: endind date of candlesticks. Example : end=None or end=20230822.
    :return: List of candlesticks in json format
    """
    valid_start, valid_end = is_valid_date_params(start, end)

    if valid_end:
        candlesticks = get_candlesticks_over_a_period(symbol, interval, valid_start, valid_end)
    else:
        candlesticks = get_candlesticks_from_a_date(symbol, interval, valid_start)

    return to_json_format(candlesticks)


def get_candlesticks_over_a_period(symbol: str, interval: str, start: str, end: str) -> List:
    row_start = f"{symbol}-{interval}#{start}"
    row_stop = f"{symbol}-{interval}#{end}"

    with pool.connection() as con:
        table = con.table(TABLE_BINANCE)
        candlesticks = [data for key, data in table.scan(row_start=row_start, row_stop=row_stop)]

    return candlesticks


def get_candlesticks_from_a_date(symbol: str, interval: str, start: str) -> List:
    row_prefix = f"{symbol}-{interval}#{start}"
    with pool.connection() as con:
        table = con.table(TABLE_BINANCE)
        candlesticks = [data for key, data in table.scan(row_prefix=row_prefix)]

    return candlesticks


def to_json_format(candlesticks: List) -> str:
    """
    Transforms list of candlesticks data to a json document.
    :param candlesticks: list of candlesticks data
    :return: a json document.
    """
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
        raise HTTPException(status_code=401, detail="Bad date format" )


def is_valid_date_params(start: str, end: str = None) -> Tuple[str, Optional[str]]:
    """
    Checks if date params are in good format, then if start date and end date are before today's date.
    :param start: start date.
    :param end: end date.
    :return: a Tuple with valid start date and end date.
    """
    date_start = str_to_datetime(start)
    if not is_date_before_today(date_start):
        raise HTTPException(status_code=402,
                            detail=f"Invalid date value, it should be before today but "
                                   f"start({start}) > today({datetime.now().strftime('%Y%m%d')})")

    if end:
        date_end = str_to_datetime(end)
        if not is_date_before_today(date_end):
            raise HTTPException(status_code=402,
                                detail=f"Invalid date value, it should be before today but "
                                       f"end({end}) > today({datetime.now().strftime('%Y%m%d')})")

        if date_start > date_end:
            tmp = start
            start = end
            end = tmp
        return start, end

    return start, None


if __name__ == "__main__":
    uvicorn.run("server_api:app", port=80, reload=True)