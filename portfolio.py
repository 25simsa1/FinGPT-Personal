# portfolio.py
import json
import os
import yfinance as yf
import pandas as pd

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        json.dump([], open(PORTFOLIO_FILE, "w"))
    with open(PORTFOLIO_FILE) as f:
        return json.load(f)

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)

def add_holding(ticker: str, shares: float, buy_price: float):
    portfolio = load_portfolio()
    existing = next((item for item in portfolio if item['ticker'] == ticker.upper()), None)
    if existing:
        existing['shares'] += shares
        existing['buy_price'] = buy_price
    else:
        portfolio.append({
            'ticker': ticker.upper(),
            'shares': shares,
            'buy_price': buy_price
        })
    save_portfolio(portfolio)
    return portfolio

def remove_holding(ticker: str):
    portfolio = load_portfolio()
    portfolio = [item for item in portfolio if item['ticker'] != ticker.upper()]
    save_portfolio(portfolio)
    return portfolio

def calculate_portfolio_value():
    portfolio = load_portfolio()
    results = []
    total_value = 0
    total_cost = 0

    for holding in portfolio:
        ticker = holding['ticker']
        shares = holding['shares']
        buy_price = holding['buy_price']
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            value = current_price * shares
            cost = buy_price * shares
            pnl = value - cost
            results.append({
                'Ticker': ticker,
                'Shares': shares,
                'Buy Price': round(buy_price, 2),
                'Current Price': round(current_price, 2),
                'Value ($)': round(value, 2),
                'P/L ($)': round(pnl, 2)
            })
            total_value += value
            total_cost += cost

    df = pd.DataFrame(results)
    total_pnl = total_value - total_cost
    summary = {
        'Total Value ($)': round(total_value, 2),
        'Total Cost ($)': round(total_cost, 2),
        'Net P/L ($)': round(total_pnl, 2)
    }
    return df, summary
