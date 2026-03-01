import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('../.secrets')

# -----------------------------
# CONFIG
# -----------------------------
MARKETSTACK_API_KEY = os.getenv('MARKETSTACK_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

client_openai = OpenAI(
    base_url="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    api_key="any-value",
    default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
)

# -----------------------------
# SERVICE 1: STOCK DATA
# -----------------------------
def get_stock_data(symbol: str):
    url = "http://api.marketstack.com/v2/eod/latest"

    params = {
        "access_key": MARKETSTACK_API_KEY,
        "symbols": symbol,
        "limit": 1,
    }

    response = requests.get(url, params=params)
    data = response.json()

    print(data)

    if "data" not in data or not data["data"]:
        return None

    stock = data["data"][0]

    return {
        "symbol": stock["symbol"],
        "price": stock["close"],
        "date": stock["date"],
        "volume": stock["volume"],
        "high": stock["high"],
        "low": stock["low"],
    }

# -----------------------------
# SERVICE 2: NEWS DATA
# -----------------------------
def get_company_news(company_name: str):
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": company_name,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params).json()

    articles = []

    for article in response.get("articles", []):
        articles.append({
            "title": article["title"],
            "description": article["description"]
        })

    return articles


# -----------------------------
# SERVICE 3: INSIGHT GENERATION
# -----------------------------
def generate_stock_insight(stock_data, news_articles):
    if not stock_data:
        return "I couldn't find stock data for that symbol."

    news_text = "\n".join(
        [f"- {n['title']}: {n['description']}" for n in news_articles]
    )

    prompt = f"""
    Stock Data:
    Symbol: {stock_data['symbol']}
    Price: {stock_data['price']}
    High: {stock_data['high']}
    Low: {stock_data['low']}
    Volume: {stock_data['volume']}

    Recent News:
    {news_text}

    Task:
    1. Summarize the stock performance in plain English
    2. Highlight trends or risks
    3. Mention if news sentiment seems positive, negative, or mixed
    """

    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a financial assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content


# -----------------------------
# MAIN SERVICE FUNCTION
# -----------------------------
def get_stock_report(symbol: str, company_name: str):
    stock = get_stock_data(symbol)
    news = get_company_news(company_name)
    insight = "Stock data unavailable from Nasdaq."

    if stock is None:
        return "Stock data unavailable from Nasdaq. Try another symbol."
    else:
        insight = generate_stock_insight(stock, news)

    return {
        "stock_data": stock,
        "news": news,
        "insight": insight
    }


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    result = get_stock_report("AAPL", "Apple")

    print("\n 📊 STOCK DATA:")
    print(result["stock_data"])

    print("\n 📰 NEWS:")
    for n in result["news"]:
        print("-", n["title"])

    print("\n 🧠 INSIGHT:")
    print(result["insight"])