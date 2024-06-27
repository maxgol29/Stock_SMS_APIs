import requests
import datetime as dt
import re
from twilio.rest import Client
import os


def weekends(today) -> tuple[int, int]:
    today_day = int(today.strftime("%w"))
    if today_day == 0:
        return (2, 3)
    elif today_day == 1:
        return (3, 4)
    elif today_day == 2:
        return (1, 4)
    else:
        return (1, 2)


date = dt.datetime.now()
YESTERDAY_DATE = date - dt.timedelta(days=weekends(date)[0])
DAY_BEFORE_YESTERDAY = date - dt.timedelta(days=weekends(date)[1])
TIME_YESTERDAY_DATE = YESTERDAY_DATE.strftime("%Y-%m-%d")
TIME_DAY_BEFORE_YESTERDAY = DAY_BEFORE_YESTERDAY.strftime("%Y-%m-%d")
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
CLEANR = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")

# API

STOCK_URL = "https://alphavantage.co/query?"
NEWS_URL = "https://newsapi.org/v2/everything?"

STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

params_stock = {
    "function": "TIME_SERIES_DAILY",
    "name": COMPANY_NAME,
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

params_news = {
    "q": COMPANY_NAME,
    "apikey": NEWS_API_KEY,
    "sortBy": "popularity"
}
response = requests.get(STOCK_URL, params_stock)
stock_data = response.json()

closed_price_yesterday = float(stock_data['Time Series (Daily)'][TIME_YESTERDAY_DATE]["4. close"])

closed_price_before_yesterday = float(
    stock_data['Time Series (Daily)'][TIME_DAY_BEFORE_YESTERDAY]["4. close"])

top_news = []
stock_reduced = True

response = requests.get(NEWS_URL, params_news)
news_data = response.json()["articles"][1:2]
for news in news_data:
    top_news.append(re.sub(CLEANR, '', news["content"]))

if closed_price_yesterday > closed_price_before_yesterday:
    stock_reduced = False

client = Client(ACCOUNT_SID, AUTH_TOKEN)

message = client.messages.create(
    from_="+123456789",  # from phone
    to="+123456789",  # to phone
    body=f"""
    {STOCK}: {["🔻", "🔺"][stock_reduced]} {round(closed_price_yesterday / closed_price_before_yesterday)}%
    {"...   ".join(map(str, top_news))}
    """
)
