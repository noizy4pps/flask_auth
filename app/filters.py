from datetime import datetime

def format_date(value, format='%Y-%m-%d'):
    return value.strftime(format) if isinstance(value, datetime) else value
