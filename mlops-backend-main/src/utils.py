from datetime import datetime, timezone

def datetime_to_string(date):
    return date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')