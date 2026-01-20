import re
from decimal import Decimal

def split_purpose(purpose: str):
    """
    Split multiple actions in one PURPOSE field
    Examples:
    'Div 30%/Bonus 1:1'
    'Dividend Rs 20 AND Bonus 1:1'
    """
    return [p.strip() for p in re.split(r"[\/;&]| AND ", purpose, flags=re.I) if p.strip()]


def classify_action(text: str):
    t = text.lower()
    if "div" in t:
        return "DIVIDEND"
    if "bonus" in t:
        return "BONUS"
    if "split" in t:
        return "SPLIT"
    return "OTHER"


def parse_dividend(text: str, face_value: Decimal):
    """
    Handles:
    - Div 30%
    - Dividend Rs 20
    """
    t = text.lower()

    # Percentage dividend (old NSE data)
    if "%" in t:
        nums = re.findall(r"\d+\.?\d*", t)
        if nums:
            return (Decimal(nums[0]) / Decimal("100")) * face_value

    # Cash dividend
    nums = re.findall(r"\d+\.?\d*", t)
    if nums:
        return Decimal(nums[0])

    return None


def parse_bonus(text: str):
    """
    Bonus 1:1 -> factor = 2
    Bonus 2:1 -> factor = 1.5
    """
    nums = re.findall(r"\d+", text)
    if len(nums) >= 2:
        a, b = Decimal(nums[0]), Decimal(nums[1])
        return (a + b) / a
    return None


def parse_split(text: str):
    """
    Split from Rs 10 to Rs 5 -> factor = 2
    """
    nums = re.findall(r"\d+", text)
    if len(nums) >= 2:
        old, new = Decimal(nums[0]), Decimal(nums[1])
        if new != 0:
            return old / new
    return None
