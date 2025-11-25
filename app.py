import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import json, os
from supabase import create_client, Client
from data_fetcher import get_stock_data, get_extended_news
from summarizer import summarize_text, analyze_sentiment
from portfolio import add_holding, remove_holding, calculate_portfolio_value
from alerts import send_email, generate_daily_summary

# --- Setup ---
st.set_page_config(page_title="FinGPT-Personal", layout="wide")

SUPABASE_URL = os.getenv("https://hjqpawkaqwpkzujyqecx.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhqcXBhd2thcXdwa3p1anlxZWN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMjgwNjksImV4cCI6MjA3OTYwNDA2OX0.Ek7IXPAwVAEyjwrIQXtxRq3g4djeC-XpMwinKVm-DCM")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.markdown("""
    <style>
    h1, h2, h3, h4 {
        color: #1E90FF;
        font-family: 'Inter', sans-serif;
    }
    .stMarkdown a { color: #008CBA !important; text-decoration: none; }
    .stMarkdown a:hover { text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

st.title("FinGPT+ : Your Private Equity Workstation")

# Sidebar Navigation
section = st.sidebar.radio("Navigate", ["AI Research Copilot", "Portfolio Tracker", "Daily Alerts Setup"])

# ===== Portfolio Tracker =====
if section == "Portfolio Tracker":
    st.header("Portfolio Tracker")

    with st.expander("➕ Add Holding"):
        ticker = st.text_input("Ticker (e.g. AAPL)", key="add_ticker")
        shares = st.number_input("Shares", min_value=0.0, step=1.0, key="add_shares")
        buy_price = st.number_input("Buy Price ($)", min_value=0.0, step=0.01, key="add_buy_price")
        if st.button("Add to Portfolio"):
            add_holding(ticker, shares, buy_price)
            st.success(f"Added {shares} shares of {ticker} @ ${buy_price}")

    portfolio_df, summary = calculate_portfolio_value()

    if not portfolio_df.empty:
        st.subheader("Your Holdings")
        st.dataframe(portfolio_df)

        st.subheader("Portfolio Summary")
        st.metric(label="Total Value ($)", value=f"{summary['Total Value ($)']:,}")
        st.metric(label="Net P/L ($)", value=f"{summary['Net P/L ($)']:,}")

        remove_ticker = st.selectbox("Remove a holding", ["None"] + list(portfolio_df['Ticker']))
        if remove_ticker != "None" and st.button("Remove"):
            remove_holding(remove_ticker)
            st.warning(f"Removed {remove_ticker} from portfolio.")
    else:
        st.info("Your portfolio is empty. Add holdings above to get started.")

# ===== AI Research Copilot =====
elif section == "AI Research Copilot":
    st.header("AI Equity Research Copilot")

    ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", "AAPL")

    if st.button("Analyze"):
        with st.spinner('Fetching market data...'):
            data = get_stock_data(ticker)

        with st.spinner('Fetching price history...'):
            hist = yf.download(ticker, period="6mo")

        with st.spinner('Fetching news...'):
            news_items = get_extended_news(ticker)

        with st.spinner('Generating summary...'):
            news_text = "\n".join([n['title'] + ': ' + n['summary'] for n in news_items])
            summary = summarize_text(ticker, data, news_text)
            sentiment = analyze_sentiment(summary)

        st.subheader(f"Fundamentals for {ticker}")
        st.dataframe(pd.DataFrame([data]))

        st.subheader("Price History (6 months)")
        st.line_chart(hist["Close"])

        st.subheader("Recent News")
        for n in news_items:
            st.markdown(f"- [{n['title']}]({n['link']})")

        st.subheader("AI Summary")
        st.text(summary)

        st.subheader("Sentiment Indicator")
        if sentiment == "positive":
            st.success("📈 Bullish sentiment detected")
        elif sentiment == "negative":
            st.error("📉 Bearish sentiment detected")
        else:
            st.info("⚖️ Neutral sentiment detected")

        score_map = {"positive": 1, "neutral": 0, "negative": -1}
        score = score_map[sentiment]
        fig, ax = plt.subplots(figsize=(4, 0.5))
        color = "green" if score > 0 else "red" if score < 0 else "gray"
        ax.barh(["Sentiment"], [score], color=color)
        ax.set_xlim(-1, 1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_frame_on(False)
        st.pyplot(fig)

# ===== Daily Alerts Setup =====
elif section == "Daily Alerts Setup":
    st.header("Daily Alerts Setup")
    st.write("Set up automatic daily email summaries of your portfolio.")

    email = st.text_input("Enter your email address")

    enable_alerts = False
    enable_sentiment_alerts = False

    # Load settings from Supabase
    if email:
        try:
            result = supabase.table("user_configs").select("*").eq("email", email).execute()
            if result.data:
                config = result.data[0]
                enable_alerts = config.get("enabled", False)
                enable_sentiment_alerts = config.get("sentiment_alerts", False)
                st.info(f"Loaded saved preferences for {email}")
        except Exception as e:
            st.error(f"Failed to load settings: {e}")

    enable_alerts = st.checkbox("Enable daily alerts", value=enable_alerts)
    enable_sentiment_alerts = st.checkbox("Enable sentiment monitoring alerts", value=enable_sentiment_alerts)

    if st.button("Save Settings"):
        config_data = {
            "email": email,
            "enabled": enable_alerts,
            "sentiment_alerts": enable_sentiment_alerts,
        }
        try:
            existing = supabase.table("user_configs").select("*").eq("email", email).execute()
            if existing.data:
                supabase.table("user_configs").update(config_data).eq("email", email).execute()
                st.success(f"✅ Updated settings for {email}")
            else:
                supabase.table("user_configs").insert(config_data).execute()
                st.success(f"✅ Saved new settings for {email}")
        except Exception as e:
            st.error(f"❌ Failed to save settings: {e}")

    st.divider()
    st.subheader("✉️ Send Test Email")
    if st.button("Send Test Email"):
        if not email:
            st.error("Please enter your email first.")
        else:
            st.info("Sending test email...")
            try:
                content, csv_path = generate_daily_summary()
                send_email(email, content)
                st.success(f"✅ Test email sent successfully to {email}!")
            except Exception as e:
                st.error(f"❌ Failed to send test email: {e}")
