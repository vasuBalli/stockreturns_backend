import pandas as pd
from django.core.management.base import BaseCommand
from core.models import StockPrice

class Command(BaseCommand):
    help = "Import stock prices from bhavcopy CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **kwargs):
        path = kwargs["csv_path"]

        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.upper()

        df = df[df["SERIES"] == "EQ"]
        df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], errors="coerce")
        df = df.dropna(subset=["SYMBOL", "TIMESTAMP", "CLOSE"])

        created = 0

        for _, row in df.iterrows():
            obj, is_created = StockPrice.objects.get_or_create(
                symbol=row["SYMBOL"].strip(),
                trade_date=row["TIMESTAMP"].date(),
                defaults={
                    "close_price": row["CLOSE"]
                }
            )

            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Stock prices imported. Rows created: {created}"
        ))
