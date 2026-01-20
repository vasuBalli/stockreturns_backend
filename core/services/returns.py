from decimal import Decimal
from datetime import datetime
from core.models import CorporateAction
from core.services.price_provider import get_close_price


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

    # Prices
    start_price = Decimal(str(get_close_price(symbol, start_date)))
    end_price = Decimal(str(get_close_price(symbol, end_date)))

    initial_value = shares * start_price

    actions = CorporateAction.objects.filter(
        symbol=symbol,
        ex_date__gt=start_date,
        ex_date__lte=end_date
    ).order_by("ex_date")

    action_log = []

    for action in actions:

        # ✅ SPLIT / BONUS
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

        # ✅ DIVIDEND (CASH ONLY)
        elif action.action_type == "DIVIDEND" and action.cash_value is not None:
            dividend_per_share = Decimal(action.cash_value)
            dividend_cash = shares * dividend_per_share
            cash += dividend_cash

            action_log.append({
                "date": action.ex_date,
                "type": "DIVIDEND_CASH",
                "dividend_per_share": float(dividend_per_share),
                "cash_received": float(dividend_cash),
                "total_cash": float(cash),
            })

    final_value = shares * end_price + cash
    gain = final_value - initial_value
    gain_pct = (gain / initial_value) * 100

    return {
        "symbol": symbol,
        "from": start_date,
        "to": end_date,

        "initial_shares": float(initial_shares),
        "final_shares": float(shares),

        "start_price": float(start_price),
        "end_price": float(end_price),

        "initial_value": float(initial_value),
        "final_value": float(final_value),

        "cash_balance": float(cash),
        "total_gain": float(gain),
        "gain_pct": float(gain_pct),

        "corporate_actions": action_log,
    }
