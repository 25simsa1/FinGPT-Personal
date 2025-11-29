# portfolio.py
import json
import os
import yfinance as yf
import pandas as pd

PORTFOLIO_FILE = "portfolio.json"


# ----------------------------
# Helper functions
# ----------------------------
def load_portfolio():
    """Load the user's portfolio from JSON."""
    if not os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump([], f)
    with open(PORTFOLIO_FILE) as f:
        return json.load(f)


def save_portfolio(portfolio):
    """Save the portfolio to JSON."""
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


# ----------------------------
# CRUD operations
# ----------------------------
def add_holding(ticker: str, shares: float, buy_price: float):
    """Add or update a holding in the portfolio."""
    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker symbol cannot be empty.")
    if shares <= 0:
        raise ValueError("Shares must be greater than zero.")
    if buy_price <= 0:
        raise ValueError("Buy price must be greater than zero.")

    portfolio = load_portfolio()
    existing = next((item for item in portfolio if item["ticker"] == ticker), None)

    if existing:
        # Update existing holding
        total_shares = existing["shares"] + shares
        existing["buy_price"] = (existing["buy_price"] * existing["shares"] + buy_price * shares) / total_shares
        existing["shares"] = total_shares
    else:
        # Add new holding
        portfolio.append({
            "ticker": ticker,
            "shares": shares,
            "buy_price": buy_price
        })

    save_portfolio(portfolio)
    return portfolio


def remove_holding(ticker: str):
    """Remove a holding by ticker."""
    portfolio = load_portfolio()
    ticker = ticker.strip().upper()
    portfolio = [item for item in portfolio if item["ticker"] != ticker]
    save_portfolio(portfolio)
    return portfolio


# ----------------------------
# Calculations
# ----------------------------
def calculate_portfolio_value():
    """Calculate total portfolio value and P/L."""
    portfolio = load_portfolio()
    results = []
    total_value = 0.0
    total_cost = 0.0

    for holding in portfolio:
        ticker = holding.get("ticker", "").strip().upper()
        shares = holding.get("shares", 0)
        buy_price = holding.get("buy_price", 0)

        if not ticker:
            print("⚠️ Skipping empty ticker entry in portfolio.json.")
            continue

        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")

            if data.empty:
                print(f"⚠️ No recent data found for {ticker}. Skipping.")
                continue

            current_price = data["Close"].iloc[-1]
            value = current_price * shares
            cost = buy_price * shares
            pnl = value - cost

            results.append({
                "Ticker": ticker,
                "Shares": shares,
                "Buy Price ($)": round(buy_price, 2),
                "Current Price ($)": round(current_price, 2),
                "Value ($)": round(value, 2),
                "P/L ($)": round(pnl, 2),
            })

            total_value += value
            total_cost += cost

        except Exception as e:
            print(f"❌ Error fetching data for {ticker}: {e}")
            continue

    df = pd.DataFrame(results)
    total_pnl = total_value - total_cost
    summary = {
        "Total Value ($)": round(total_value, 2),
        "Total Cost ($)": round(total_cost, 2),
        "Net P/L ($)": round(total_pnl, 2),
    }

    return df, summary