# core/services/nse_price_provider.py

import requests
import pandas as pd
import zipfile
import io
from datetime import datetime
from datetime import timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nseindia.com",
    "Accept": "*/*"
}


def download_bhavcopy(date: str):
    dt = datetime.strptime(date, "%Y-%m-%d")

    urls = [
        # New format
        f"https://archives.nseindia.com/content/cm/"
        f"BhavCopy_NSE_CM_0_0_0_{dt.strftime('%Y%m%d')}_F_0000.csv.zip",

        # Old fallback format
        f"https://archives.nseindia.com/content/cm/"
        f"cm{dt.strftime('%d%b%Y').upper()}bhav.csv.zip"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                continue

            if not r.content.startswith(b"PK"):
                continue

            z = zipfile.ZipFile(io.BytesIO(r.content))
            csv_file = z.namelist()[0]

            df = pd.read_csv(z.open(csv_file))

            df.columns = (
                df.columns.astype(str)
                .str.upper()
                .str.strip()
            )

            return df

        except Exception:
            continue

    return None


def get_stock_price(symbol: str, date: str):
    """
    Returns NSE official price for given symbol and date.
    """

    trading_date = get_previous_trading_day(date)
    df = download_bhavcopy(trading_date)

    if df is None:
        raise ValueError(f"Bhavcopy not found for {trading_date}")

  

    symbol = symbol.upper().strip()

    column_map = {
        "SYMBOL": ["SYMBOL", "TCKRSYMB", "SC_NAME"],
        "SERIES": ["SERIES", "SCTYSRS"],
        "OPEN": ["OPEN_PRICE", "OPEN", "OPNPRIC"],
        "HIGH": ["HIGH_PRICE", "HIGH", "HGHPRIC"],
        "LOW": ["LOW_PRICE", "LOW", "LWPRIC"],
        "CLOSE": ["CLOSE_PRICE", "CLOSE", "CLSPRIC"],
        "VOLUME": ["TTL_TRD_QNTY", "TOTTRDQTY", "TTLTRADGVOL"]
    }

    def find(keys):
        for k in keys:
            if k in df.columns:
                return k
        return None

    symbol_col = find(column_map["SYMBOL"])
    series_col = find(column_map["SERIES"])
    close_col = find(column_map["CLOSE"])

    if not symbol_col or not close_col:
        raise ValueError(f"Unsupported NSE structure: {list(df.columns)}")

    df[symbol_col] = df[symbol_col].astype(str).str.upper().str.strip()
    stock = df[df[symbol_col] == symbol]

    if series_col:
        df[series_col] = df[series_col].astype(str).str.upper().str.strip()
        stock = stock[stock[series_col] == "EQ"]

    if stock.empty:
        raise ValueError(f"{symbol} not found on {date}")

    row = stock.iloc[0]

    return float(row[close_col])


def get_previous_trading_day(date: str, max_lookback: int = 10):
    """
    Finds the nearest previous trading day (including given date)
    by checking bhavcopy availability.
    """
    dt = datetime.strptime(date, "%Y-%m-%d")

    for _ in range(max_lookback):
        df = download_bhavcopy(dt.strftime("%Y-%m-%d"))
        if df is not None:
            return dt.strftime("%Y-%m-%d")

        dt -= timedelta(days=1)

    raise ValueError(f"No trading day found before {date}")
