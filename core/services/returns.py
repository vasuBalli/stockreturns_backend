from decimal import Decimal
from datetime import datetime
from core.models import CorporateAction
from core.services.price_resolver import get_stock_price


def calculate_portfolio_return(
    symbol,
    start_date,
    end_date,
    initial_shares,
):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    shares = Decimal(str(initial_shares))
    cash = Decimal("0")

    # Prices (NSE → Yahoo fallback handled inside resolver)
    start_price = Decimal(
        str(get_stock_price(symbol, start_date.strftime("%Y-%m-%d")))
    )
    end_price = Decimal(
        str(get_stock_price(symbol, end_date.strftime("%Y-%m-%d")))
    )

    initial_value = shares * start_price

    actions = CorporateAction.objects.filter(
        symbol=symbol,
        ex_date__gt=start_date,
        ex_date__lte=end_date
    ).order_by("ex_date")

    action_log = []

    for action in actions:

        # SPLIT / BONUS → affects shares only
        if action.action_type in ("SPLIT", "BONUS") and action.factor:
            old_shares = shares
            shares *= Decimal(action.factor)

            action_log.append({
                "date": action.ex_date,
                "type": action.action_type,
                "factor": float(action.factor),
                "shares_before": float(old_shares),
                "shares_after": float(shares),
            })

        # DIVIDEND → CASH ONLY
        elif action.action_type == "DIVIDEND" and action.cash_value is not None:
            dividend_cash = shares * Decimal(action.cash_value)
            cash += dividend_cash

            action_log.append({
                "date": action.ex_date,
                "type": "DIVIDEND_CASH",
                "dividend_per_share": float(action.cash_value),
                "cash_received": float(dividend_cash),
                "total_cash": float(cash),
            })

    # -------------------------
    # 🔹 CLEAN FINANCIAL METRICS
    # -------------------------

    # Price-only gain (NO dividends)
    price_gain = (end_price - start_price) * shares
    price_gain_pct = (
        (end_price - start_price) / start_price
    ) * 100

    # Dividend-only gain
    dividend_gain = cash

    # Total gain = price gain + dividends
    total_gain = price_gain + dividend_gain
    total_gain_pct = (total_gain / initial_value) * 100

    final_value = initial_value + total_gain

    return {
        "symbol": symbol,
        "from": start_date,
        "to": end_date,

        "initial_shares": float(initial_shares),
        "final_shares": float(shares),

        "start_price": float(start_price),
        "end_price": float(end_price),

        "initial_value": float(initial_value),

        # ✅ PRICE-ONLY
        "price_gain": float(price_gain),
        "price_gain_pct": float(price_gain_pct),

        # ✅ DIVIDENDS (SEPARATE)
        "dividend_gain": float(dividend_gain),

        # ✅ TOTAL (EXPLICIT)
        "total_gain": float(total_gain),
        "total_gain_pct": float(total_gain_pct),

        "final_value": float(final_value),

        "corporate_actions": action_log,
    }
