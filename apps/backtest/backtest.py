from fastapi import FastAPI, HTTPException
from typing import Optional, List, Tuple
import pandas as pd
import uvicorn

app = FastAPI(title="OPA Backtesting engine",
              description="An API to backtest your trading strategy")

if __name__ == "__main__":
    uvicorn.run("backtest:app", port=5052, reload=True)