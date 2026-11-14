import re


def normalize_phone(raw: str) -> str:
    """Digits only, with Nigerian local format (0801...) converted to 234801..."""
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("0") and len(digits) == 11:
        digits = "234" + digits[1:]
    return digits
