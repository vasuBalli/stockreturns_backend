from django.db import models

class StockPrice(models.Model):
    symbol = models.CharField(max_length=20, db_index=True)
    trade_date = models.DateField(db_index=True)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("symbol", "trade_date")
        indexes = [
            models.Index(fields=["symbol", "trade_date"]),
        ]


class CorporateAction(models.Model):
    ACTION_CHOICES = [
        ("DIVIDEND", "Dividend"),
        ("SPLIT", "Split"),
        ("BONUS", "Bonus"),
        ("OTHER", "Other"),
    ]

    symbol = models.CharField(max_length=20, db_index=True)
    ex_date = models.DateField(db_index=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)

    factor = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True
    )

    cash_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    raw_purpose = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["symbol", "ex_date"]),
        ]

