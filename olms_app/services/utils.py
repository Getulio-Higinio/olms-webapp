from datetime import date
import pandas as pd

def safe_float(value):
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except Exception:
        return None

def safe_date(value):
    if value is None or value == "":
        return None
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None

def expiry_status(bbd):
    if not bbd:
        return ""
    days = (bbd - date.today()).days
    if days < 0:
        return "EXPIRED"
    if days <= 30:
        return "CRITICAL"
    if days <= 90:
        return "WARNING"
    return "OK"
