from core.services.nse_price_provider import get_stock_price as nse_price
from core.services.yahoo_price_provider import get_stock_price_yahoo

def get_stock_price(symbol: str, date: str):
    """
    Unified price resolver:
    1. Try NSE bhavcopy
    2. Fallback to Yahoo Finance
    """

    try:
        return nse_price(symbol, date)
    except Exception as nse_error:
        try:
            return get_stock_price_yahoo(symbol, date)
        except Exception as yahoo_error:
            raise ValueError(
                f"Price not available for {symbol} on or before {date}"
            )
