import yfinance as yf
import requests

def get_stock_data(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        'Company': info.get('shortName', ''),
        'Market Cap': info.get('marketCap', ''),
        'P/E Ratio': info.get('trailingPE', ''),
        'EPS': info.get('trailingEps', ''),
        'Sector': info.get('sector', ''),
        '52w High': info.get('fiftyTwoWeekHigh', ''),
        '52w Low': info.get('fiftyTwoWeekLow', '')
    }

def get_news(ticker: str):
    try:
        url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&apiKey=YOUR_NEWSAPI_KEY"
        r = requests.get(url)
        data = r.json()
        return [
            {'title': a['title'], 'summary': a.get('description', ''), 'link': a['url']}
            for a in data.get('articles', [])[:3]
        ]
    except Exception as e:
        print("Error fetching news:", e)
        return []
