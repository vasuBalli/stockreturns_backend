# core/services/price_provider.py

import yfinance as yf
import pandas as pd
from datetime import timedelta

def get_close_price(symbol: str, date):
    """
    Returns last available close price ON or BEFORE the given date.
    Guaranteed to return a number or raise error.
    """
    yf_symbol = f"{symbol}.NS"

    start = pd.to_datetime(date) - timedelta(days=7)
    end = pd.to_datetime(date) + timedelta(days=1)

    df = yf.download(
        yf_symbol,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        progress=False
    )

    if df.empty:
        raise ValueError(f"No price data for {symbol}")

    df = df[df.index <= pd.to_datetime(date)]

    if df.empty:
        raise ValueError(f"No trading price before {date}")

    return float(df["Close"].iloc[-1])
