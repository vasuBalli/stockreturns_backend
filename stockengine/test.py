import requests
import pandas as pd
import zipfile
import io
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nseindia.com",
    "Accept": "*/*"
}


def download_bhavcopy(date: str):
    dt = datetime.strptime(date, "%Y-%m-%d")

    urls = [
        # equity cash bhavcopy
        f"https://archives.nseindia.com/content/cm/"
        f"BhavCopy_NSE_CM_0_0_0_{dt.strftime('%Y%m%d')}_F_0000.csv.zip",

        # fallback old
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

    df = download_bhavcopy(date)

    if df is None:
        return {"status": "error", "message": "Bhavcopy not found"}

    symbol = symbol.upper().strip()

    # ---- column detection ----
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
    open_col = find(column_map["OPEN"])
    high_col = find(column_map["HIGH"])
    low_col = find(column_map["LOW"])
    close_col = find(column_map["CLOSE"])
    volume_col = find(column_map["VOLUME"])

    if not symbol_col or not close_col:
        return {
            "status": "error",
            "message": f"Unsupported NSE structure: {list(df.columns)}"
        }

    df[symbol_col] = df[symbol_col].astype(str).str.upper().str.strip()

    stock = df[df[symbol_col] == symbol]

    if series_col:
        df[series_col] = df[series_col].astype(str).str.upper().str.strip()
        stock = stock[stock[series_col] == "EQ"]

    if stock.empty:
        return {
            "status": "error",
            "message": f"{symbol} not found on {date}"
        }

    row = stock.iloc[0]

    return {
        "status": "success",
        "symbol": symbol,
        "date": date,
        "open": float(row[open_col]) if open_col else None,
        "high": float(row[high_col]) if high_col else None,
        "low": float(row[low_col]) if low_col else None,
        "close": float(row[close_col]),
        "volume": float(row[volume_col]) if volume_col else None
    }


# ------------------
# TEST
# ------------------
if __name__ == "__main__":
    print(get_stock_price("INFY", "2025-01-22"))
