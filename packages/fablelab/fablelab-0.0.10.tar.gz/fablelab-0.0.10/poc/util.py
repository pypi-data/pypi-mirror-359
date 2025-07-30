import pytz
from datetime import datetime, timedelta

def datetime_sub(days=0):
    korean_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korean_tz) - timedelta(days=days)

def format_yesterday(format='%Y%m%d'):
    return datetime_sub(1).strftime(format)