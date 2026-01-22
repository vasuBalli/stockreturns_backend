import yfinance as yf
import pandas as pd
from datetime import timedelta

def get_stock_price_yahoo(symbol: str, date: str):
    """
    Yahoo fallback price provider.
    Returns last available close <= date.
    """

    yf_symbol = f"{symbol}.NS"
    target_date = pd.to_datetime(date)

    start = target_date - timedelta(days=10)
    end = target_date + timedelta(days=1)

    df = yf.download(
        yf_symbol,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        progress=False
    )

    if df.empty:
        raise ValueError("Yahoo price data not found")

    df = df[df.index <= target_date]

    if df.empty:
        raise ValueError("Yahoo price not found before date")

    return float(df["Close"].iloc[-1])
