from django.contrib import admin
from .models import StockPrice, CorporateAction

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ("symbol", "trade_date", "close_price")
    list_filter = ("symbol",)


@admin.register(CorporateAction)
class CorporateActionAdmin(admin.ModelAdmin):
    list_display = ("symbol", "ex_date", "action_type", "factor", "cash_value")
    list_filter = ("symbol", "action_type")
