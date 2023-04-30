import datetime as dt
def dt_now():
    return dt.datetime.utcnow() - dt.timedelta(hours=3)