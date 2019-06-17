from datetime import datetime, timedelta
import load_settings
import pytz
import requests

settings = load_settings.load()
timezone = pytz.timezone(settings["timezone"])

twitterDateFormat = "%a %b %d %H:%M:%S %z %Y"
apiDateFormat = "%Y-%m-%d"


def getFinalUrl(url):
    try:
        r = requests.get(url)
        return r.url
    except:
        return ""


def printDateOnly(date):
    date_in_tz = date.astimezone(timezone)
    return datetime.strftime(date, "%Y-%m-%d")


def printDate(date):
    if date is None:
        return ""
    date_in_tz = date.astimezone(timezone)
    return datetime.strftime(date, "%Y-%m-%d %H:%M:%S")


def parseDate(dateString):
    d = datetime.strptime(dateString, apiDateFormat)
    return datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond, timezone)


def parseTwitterDate(dateString):
    return datetime.strptime(dateString, twitterDateFormat)


def betweenDates(x, start, end):
    return start <= x and x <= end


def excel_date(date1):
    temp = dt.datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = date1 - temp
    return float(delta.days) + (float(delta.seconds) / 86400)
