# data_fetcher.py
import os
import yfinance as yf
import requests
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# --- Constants ---
FMP_API_KEY = os.getenv("FMP_API_KEY")
FMP_BASE = "https://financialmodelingprep.com/api/v3"

# ================================================================
#  NEWS AGGREGATION
# ================================================================
def get_extended_news(ticker: str):
    """Fetch news from NewsAPI + Google News RSS + Finviz headlines."""
    news_items = []

    # 1️⃣ NewsAPI
    news_api_key = os.getenv("NEWS_API_KEY")
    if news_api_key:
        try:
            url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey={news_api_key}"
            data = requests.get(url, timeout=10).json()
            for a in data.get("articles", [])[:3]:
                news_items.append({
                    "title": a["title"],
                    "summary": a.get("description", ""),
                    "source": a["source"]["name"],
                    "link": a["url"]
                })
        except Exception as e:
            print(f"NewsAPI fetch error for {ticker}: {e}")

    # 2️⃣ Google News RSS
    try:
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={ticker}+stock")
        for entry in feed.entries[:3]:
            news_items.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "source": "Google News",
                "link": entry.link
            })
    except Exception as e:
        print(f"Google News RSS error for {ticker}: {e}")

    # 3️⃣ Finviz headlines (light scraping)
    try:
        finviz_url = f"https://finviz.com/quote.ashx?t={ticker}"
        html = requests.get(finviz_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
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
    except Exception as e:
        print(f"Finviz fetch error for {ticker}: {e}")

    return news_items

# ================================================================
#  STOCK DATA (yfinance + FMP)
# ================================================================
@st.cache_data(ttl=3600)
def get_stock_data(ticker: str):
    """Fetch stock metrics using yfinance and supplement with Financial Modeling Prep fundamentals."""
    # --- yfinance data ---
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
    except Exception as e:
        print(f"yfinance error for {ticker}: {e}")
        info = {}

    data = {
        'Company': info.get('shortName', ''),
        'Market Cap': info.get('marketCap', ''),
        'P/E Ratio': info.get('trailingPE', ''),
        'EPS': info.get('trailingEps', ''),
        'Sector': info.get('sector', ''),
        '52w High': info.get('fiftyTwoWeekHigh', ''),
        '52w Low': info.get('fiftyTwoWeekLow', ''),
    }

    # --- Financial Modeling Prep fundam