from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.services.returns import calculate_portfolio_return


@api_view(["GET"])
def returns_api(request):
    symbol = request.GET.get("symbol")
    start = request.GET.get("from")
    end = request.GET.get("to")

    shares = Decimal(request.GET.get("shares", "1"))

    if not symbol or not start or not end:
        return Response(
            {"error": "symbol, from, to are required"},
            status=400
        )

    result = calculate_portfolio_return(
        symbol=symbol,
        start_date=start,
        end_date=end,
        initial_shares=shares,
    )

    return Response(result)
