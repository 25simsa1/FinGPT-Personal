 # data_fetcher.py
import os
import requests
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")

@st.cache_data(ttl=3600)
def get_stock_data(ticker: str):
    """Fetch company fundamentals using Alpha Vantage Overview + Income Statement."""
    data = {}
    if not ALPHA_KEY:
        print("Missing ALPHA_VANTAGE_KEY")
        return data

    try:
        # --- Company Overview ---
        overview = requests.get(
            f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_KEY}",
            timeout=10
        ).json()
        if "Symbol" in overview:
            data = {
                "Company": overview.get("Name", ticker),
                "Sector": overview.get("Sector", ""),
                "Industry": overview.get("Industry", ""),
                "Market Cap ($)": overview.get("MarketCapitalization", ""),
                "P/E Ratio": overview.get("PERatio", ""),
                "EPS": overview.get("EPS", ""),
                "Dividend Yield": overview.get("DividendYield", ""),
                "Beta": overview.get("Beta", ""),
                "52w High": overview.get("52WeekHigh", ""),
                "52w Low": overview.get("52WeekLow", "")
            }

        # --- Income Statement for EBITDA ---
        income = requests.get(
            f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={ALPHA_KEY}",
            timeout=10
        ).json()
        if "annualReports" in income and len(income["annualReports"]) > 0:
            latest = income["annualReports"][0]
            data["EBITDA ($)"] = latest.get("ebitda", "")
            data["Revenue ($)"] = latest.get("totalRevenue", "")
            data["Net Income ($)"] = latest.get("netIncome", "")
    except Exception as e:
        print(f"⚠️ Alpha Vantage fundamentals error for {ticker}: {e}")

    return data


def get_extended_news(ticker: str):
    """Fetch recent news headlines from Google News RSS and Finviz."""
    news_items = []

    # Google News
    try:
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={ticker}+stock")
        for entry in feed.entries[:5]:
            news_items.append({
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "source": "Google News",
                "link": entry.link
            })
    except Exception as e:
        print(f"Google News RSS error for {ticker}: {e}")

    # Finviz headlines
    try:
        finviz_url = f"https://finviz.com/quote.ashx?t={ticker}"
        html = requests.get(finviz_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find(id="news-table")
        if table:
            for row in table.find_all("tr")[:5]:
                news_items.append({
                    "title": row.a.text,
                    "summary": "(via Finviz)",
                    "source": "Finviz",
                    "link": row.a["href"]
                })
    except Exception as e:
        print(f"Finviz fetch error for {ticker}: {e}")

    return news_items
