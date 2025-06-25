from datetime import datetime
from flask_babel import lazy_gettext as _

def format_date(value, format='%Y-%m-%d'):
    return value.strftime(format) if isinstance(value, datetime) else value

def relative_time(value):
    if not isinstance(value, datetime):
        return value

    now = datetime.utcnow()
    diff = now - value

    seconds = int(diff.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days

    if seconds < 60:
        return _("just now")
    elif minutes < 60:
        return _("%(min)d minute(s) ago", min=minutes)
    elif hours < 24:
        return _("%(hr)d hour(s) ago", hr=hours)
    elif days < 30:
        return _("%(day)d day(s) ago", day=days)
    else:
        return value.strftime('%Y-%m-%d')  # fallback to full date
