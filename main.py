import requests
from datetime import datetime
import os
from twilio.rest import Client


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

NEWS_END_POINT = "https://newsapi.org/v2/everything?"
ALPHA_END_POINT = "https://www.alphavantage.co/query"

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

# NUMBERS

FROM_NUMBER = os.environ.get("FROM_NUMBER")
TO_NUMBER = os.environ.get("TO_NUMBER")


# KEYS
news_api_key = os.environ.get("NEWS_API_KEY")
alpha_key = os.environ.get("ALPHA_KEY")

# DATE
now = datetime.now()
present_year = now.year
present_month = now.month
present_day = now.day
current_date = f"{present_year}-{present_month}-{present_day}"
previous_date = f"{present_year}-{present_month}-{present_day - 1}"

## STEP 1: Use https://newsapi.org
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").


alpha_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": alpha_key
}
news_parameters = {
    "qInTitle": COMPANY_NAME,
    "apiKey": news_api_key
}
account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN

response = requests.get(url=ALPHA_END_POINT, params=alpha_parameters)
response.raise_for_status()
stock_data = response.json()["Time Series (Daily)"]

stock_data_list = [value["4. close"] for (key, value) in stock_data.items()]
stock_data_slicing = stock_data_list[:3]

yesterday_price = float(stock_data_slicing[1])
a_day_after_price = float(stock_data_slicing[2])

difference = yesterday_price - a_day_after_price
percentage = difference / yesterday_price * 100
total = round(percentage)

if total > 0:
    stock_value = "🔺"
else:
    stock_value = "🔻"


total = abs(total)

if 0 < total <= 5:
    response = requests.get(url=NEWS_END_POINT, params=news_parameters)
    response.raise_for_status()
    article_data = response.json()["articles"]
    news_slicing = article_data[:3]
    # news_list = [{"title": news["title"], "description": news["description"]} for news in news_slicing]
    for news in news_slicing:
        news_title = news["title"]
        news_description = news["description"]
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
            body=f"{STOCK}: {stock_value}{total}%\n"
                f"Headline: {news_title}\n"
                 f"Brief: {news_description}",
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )

        print(message.status)
        # print(f"{STOCK}: {stock_value}{total}%\n"
        #     f"Headline: {news_title}\n"
        #       f"Brief: {news_description}\n")




## STEP 2: Use https://www.alphavantage.co
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

