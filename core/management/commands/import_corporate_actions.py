import pandas as pd
from decimal import Decimal
from django.core.management.base import BaseCommand
from core.models import CorporateAction
from core.utils.corporate_action_parser import (
    split_purpose,
    classify_action,
    parse_dividend,
    parse_bonus,
    parse_split,
)

class Command(BaseCommand):
    help = "Import NSE corporate actions from CSV"

    def handle(self, *args, **kwargs):
        path = "actions.csv"

        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.upper()

        df = df[df["SERIES"] == "EQ"]
        df["EX-DATE"] = pd.to_datetime(df["EX-DATE"], errors="coerce")
        df = df.dropna(subset=["SYMBOL", "EX-DATE", "PURPOSE"])

        created = 0

        for _, row in df.iterrows():
            symbol = row["SYMBOL"].strip()
            ex_date = row["EX-DATE"].date()
            purpose = str(row["PURPOSE"]).strip()
            face_value = Decimal(str(row.get("FACE VALUE", 0) or 0))

            for part in split_purpose(purpose):
                action_type = classify_action(part)

                factor = None
                cash_value = None

                if action_type == "DIVIDEND":
                    cash_value = parse_dividend(part, face_value)

                elif action_type == "BONUS":
                    factor = parse_bonus(part)

                elif action_type == "SPLIT":
                    factor = parse_split(part)

                if action_type == "OTHER":
                    continue

                obj, is_created = CorporateAction.objects.get_or_create(
                    symbol=symbol,
                    ex_date=ex_date,
                    action_type=action_type,
                    raw_purpose=part,
                    defaults={
                        "factor": factor,
                        "cash_value": cash_value,
                    },
                )

                if is_created:
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Corporate actions imported. Rows created: {created}"
        ))
