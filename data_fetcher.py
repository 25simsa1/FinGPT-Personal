import os
import yfinance as yf
import requests
import feedparser
from bs4 import BeautifulSoup
from alpha_vantage.fundamentaldata import FundamentalData

def get_extended_news(ticker: str):
    """Fetch news from NewsAPI + Google News RSS + Finviz headlines."""
    news_items = []

    # 1️⃣ NewsAPI
    url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={os.getenv('NEWS_API_KEY')}"
    data = requests.get(url).json()
    for a in data.get("articles", [])[:3]:
        news_items.append({
            "title": a["title"],
            "summary": a.get("description", ""),
            "source": a["source"]["name"],
            "link": a["url"]
        })

    # 2️⃣ Google News RSS
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={ticker}+stock")
    for entry in feed.entries[:3]:
        news_items.append({
            "title": entry.title,
            "summary": entry.get("summary", ""),
            "source": "Google News",
            "link": entry.link
        })

    # 3️⃣ Finviz headlines (light scraping)
    finviz_url = f"https://finviz.com/quote.ashx?t={ticker}"
    html = requests.get(finviz_url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "html.parser")
    news_table = soup.find(id="news-table")
    if news_table:
        for row in news_table.find_all("tr")[:3]:
            link = row.a["href"]
            title = row.a.text
            news_items.append({
                "title": title,
                "summary": "(via Finviz)",
                "source": "Finviz",
                "link": link
            })

    return news_items


def get_stock_data(ticker: str):
    """Fetch stock metrics using yfinance and supplement with Alpha Vantage fundamentals."""
    stock = yf.Ticker(ticker)
    info = stock.info

    data = {
        'Company': info.get('shortName', ''),
        'Market Cap': info.get('marketCap', ''),
        'P/E Ratio': info.get('trailingPE', ''),
        'EPS': info.get('trailingEps', ''),
        'Sector': info.get('sector', ''),
        '52w High': info.get('fiftyTwoWeekHigh', ''),
        '52w Low': info.get('fiftyTwoWeekLow', '')
    }

    try:
        fd = FundamentalData(os.getenv("ALPHA_VANTAGE_KEY"), output_format='pandas')
        av_data, _ = fd.get_company_overview(ticker)
        for key in ["BookValue", "DividendPerShare", "EBITDA", "RevenueTTM", "ProfitMargin"]:
            if key in av_data.columns:
                data[key] = av_data[key].iloc[0]
    except Exception as e:
        print(f"Alpha Vantage fetch error for {ticker}: {e}")

    return data
