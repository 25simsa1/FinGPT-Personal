# app.py
import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import json, os, re
from dotenv import load_dotenv
from alpha_vantage.timeseries import TimeSeries

# --- Load environment ---
load_dotenv()

# =====================================================
# SAFE DATA FETCHER (Alpha Vantage ONLY)
# =====================================================
@st.cache_data(ttl=3600)
def safe_download(ticker, period="6mo"):
    """
    Fetch historical daily stock data from Alpha Vantage (compact for free-tier).
    """
    import pandas as pd
    import os

    ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")
    if not ALPHA_KEY:
        st.error("Missing ALPHA_VANTAGE_KEY in .env file.")
        return pd.DataFrame()

    try:
        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")
        data, meta = ts.get_daily(symbol=ticker, outputsize="compact")  # ~100 days
        data = data.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        data.index = pd.to_datetime(data.index)
        data = data.sort_index()
        print(f"✅ Loaded {len(data)} rows from Alpha Vantage for {ticker}")
        return data
    except Exception as e:
        print(f"❌ Alpha Vantage error for {ticker}: {e}")
        return pd.DataFrame()


# =====================================================
# IMPORTS FOR APP FUNCTIONALITY
# =====================================================
from supabase import create_client, Client
from data_fetcher import get_stock_data, get_extended_news
from summarizer import summarize_text, analyze_sentiment
from portfolio import add_holding, remove_holding, calculate_portfolio_value
from alerts import send_email, generate_daily_summary


# =====================================================
# STREAMLIT SETUP
# =====================================================
st.set_page_config(page_title="FinGPT-Personal", layout="wide")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("⚠️ Supabase credentials missing. Please set SUPABASE_URL and SUPABASE_KEY in your environment.")
    supabase = None


# =====================================================
# CUSTOM STYLING
# =====================================================
st.markdown("""
    <style>
    h1, h2, h3, h4 {
        color: #1E90FF;
        font-family: 'Inter', sans-serif;
    }
    p, strong {
        font-family: 'Inter', sans-serif !important;
    }
    .stMarkdown a { color: #008CBA !important; text-decoration: none; }
    .stMarkdown a:hover { text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

st.title("FinGPT+ : Your Private Equity Workstation")

# Sidebar navigation
section = st.sidebar.radio("Navigate", ["AI Research Copilot", "Portfolio Tracker", "Daily Alerts Setup"])

# =====================================================
# PORTFOLIO TRACKER
# =====================================================
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


# =====================================================
# AI RESEARCH COPILOT
# =====================================================
elif section == "AI Research Copilot":
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    st.header("AI Equity Research Copilot")

    ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", "AAPL").upper()
    period = st.selectbox("Select Price History Range", ["1mo", "3mo", "6mo", "1y"], index=2)

    # Indicators
    st.markdown("**Indicators**")
    col_ind1, col_ind2, col_ind3 = st.columns(3)
    with col_ind1:
        show_ma = st.checkbox("Moving Averages (50 & 200)", value=True)
    with col_ind2:
        show_rsi = st.checkbox("RSI (14)", value=True)
    with col_ind3:
        show_macd = st.checkbox("MACD (12, 26, 9)", value=True)

    if st.button("Analyze"):
        with st.spinner('Fetching fundamentals...'):
            data = get_stock_data(ticker)

        with st.spinner(f'Fetching {period} price history...'):
            hist = safe_download(ticker, period)

        if hist.empty:
            st.warning("No historical data found for this ticker / period.")
            st.stop()

        with st.spinner('Fetching latest news...'):
            news_items = get_extended_news(ticker)

        with st.spinner('Generating AI summary...'):
            news_text = "\n".join([f"{n['title']}: {n['summary']}" for n in news_items])
            summary = summarize_text(ticker, data, news_text)
            sentiment = analyze_sentiment(summary)

        st.subheader(f"Fundamentals for {ticker}")
        if data:
            fundamentals_df = pd.DataFrame([data]).T
            fundamentals_df.columns = ["Value"]
            st.table(fundamentals_df)
        else:
            st.info("No fundamental data available.")

        # --- Chart ---
        st.subheader(f"Price History ({period}) — Interactive Chart")

        if show_ma and len(hist) >= 50:
            hist["MA50"] = hist["Close"].rolling(window=50).mean()
        if show_ma and len(hist) >= 200:
            hist["MA200"] = hist["Close"].rolling(window=200).mean()

        # RSI
        delta = hist["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss
        hist["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        fast_ema = hist["Close"].ewm(span=12, adjust=False).mean()
        slow_ema = hist["Close"].ewm(span=26, adjust=False).mean()
        hist["MACD"] = fast_ema - slow_ema
        hist["Signal"] = hist["MACD"].ewm(span=9, adjust=False).mean()
        hist["MACD_Hist"] = hist["MACD"] - hist["Signal"]

        # Plotly chart
        subplot_titles = ["Price (Candlesticks)", "Volume"]
        row_heights = [0.5, 0.2]
        if show_rsi:
            subplot_titles.append("RSI (14)")
            row_heights.append(0.15)
        if show_macd:
            subplot_titles.append("MACD (12, 26, 9)")
            row_heights.append(0.15)

        fig = make_subplots(
            rows=len(subplot_titles),
            cols=1,
            shared_xaxes=True,
            row_heights=row_heights,
            vertical_spacing=0.03,
            subplot_titles=tuple(subplot_titles)
        )

        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist['Open'], high=hist['High'],
            low=hist['Low'], close=hist['Close'],
            name='Price', increasing_line_color="green", decreasing_line_color="red"
        ), row=1, col=1)

        if show_ma and "MA50" in hist:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["MA50"], line=dict(color="blue"), name="MA50"), row=1, col=1)
        if show_ma and "MA200" in hist:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["MA200"], line=dict(color="orange"), name="MA200"), row=1, col=1)

        vol_colors = ["green" if c >= o else "red" for o, c in zip(hist["Open"], hist["Close"])]
        fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], marker_color=vol_colors, name="Volume"), row=2, col=1)

        if show_rsi:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["RSI"], line=dict(color="purple"), name="RSI"), row=3, col=1)
        if show_macd:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["MACD"], line=dict(color="blue"), name="MACD"), row=len(subplot_titles), col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Signal"], line=dict(color="orange"), name="Signal"), row=len(subplot_titles), col=1)
            fig.add_trace(go.Bar(x=hist.index, y=hist["MACD_Hist"], name="MACD Hist", opacity=0.4), row=len(subplot_titles), col=1)

        fig.update_layout(height=900, template="plotly_white", title=f"{ticker} — Price, Volume, RSI & MACD ({period})")
        st.plotly_chart(fig, use_container_width=True)

        # --- Recent News ---
        st.subheader("Recent News")
        for n in news_items:
            st.markdown(f"- [{n['title']}]({n['link']})")

        # --- AI Summary (CLEAN RENDER) ---
        st.subheader("AI Summary")

        def clean_html(raw_text):
            """Remove HTML tags and entities the AI might include."""
            raw_text = re.sub(r"<[^>]+>", "", raw_text)  # Remove tags
            raw_text = re.sub(r"&[a-z]+;", "", raw_text)  # Remove entities
            return raw_text.strip()

        # Clean any stray HTML from the AI response
        cleaned_summary = clean_html(summary)
        
        # Split by double newlines (as formatted by summarizer.py)
        paragraphs = [p.strip() for p in cleaned_summary.split("\n\n") if p.strip()]
        
        # Assign paragraphs to sections
        overview = paragraphs[0] if len(paragraphs) > 0 else ""
        developments = paragraphs[1] if len(paragraphs) > 1 else ""
        risks = paragraphs[2] if len(paragraphs) > 2 else ""

        # Build styled output (no leading whitespace)
        styled_summary = '<div style="font-family: \'Inter\', \'Arial\', sans-serif; font-size: 16px; line-height: 1.7; color: #e0e0e0; background-color: rgba(255, 255, 255, 0.02); border-left: 4px solid #1E90FF; padding: 1.5rem 1.5rem; border-radius: 10px; text-align: justify; white-space: normal; word-wrap: break-word;">'
        
        if overview:
            styled_summary += f'<p style="margin-bottom: 1.2rem;"><strong style="color: #1E90FF;">Overview</strong><br>{overview}</p>'
        
        if developments:
            styled_summary += f'<p style="margin-bottom: 1.2rem;"><strong style="color: #1E90FF;">Recent Developments</strong><br>{developments}</p>'
        
        if risks:
            styled_summary += f'<p style="margin-bottom: 0;"><strong style="color: #1E90FF;">Risks & Outlook</strong><br>{risks}</p>'
        
        styled_summary += '</div>'

        st.markdown(styled_summary, unsafe_allow_html=True)

        # --- Sentiment Indicator ---
        st.subheader("Sentiment Indicator")
        if sentiment == "positive":
            st.success("Bullish sentiment detected")
        elif sentiment == "negative":
            st.error("Bearish sentiment detected")
        else:
            st.info("Neutral sentiment detected")

        score_map = {"positive": 1, "neutral": 0, "negative": -1}
        score = score_map[sentiment]
        fig_sent, ax = plt.subplots(figsize=(4, 0.5))
        ax.barh(["Sentiment"], [score], color="green" if score > 0 else "red" if score < 0 else "gray")
        ax.set_xlim(-1, 1)
        ax.set_yticks([]); ax.set_xticks([]); ax.set_frame_on(False)
        st.pyplot(fig_sent)


# =====================================================
# DAILY ALERTS SETUP
# =====================================================
elif section == "Daily Alerts Setup":
    st.header("Daily Alerts Setup")
    st.write("Set up automatic daily email summaries of your portfolio.")

    email = st.text_input("Enter your email address")
    enable_alerts = st.checkbox("Enable daily alerts")
    enable_sentiment_alerts = st.checkbox("Enable sentiment monitoring alerts")

    if st.button("Save Settings"):
        if supabase and email:
            config_data = {"email": email, "enabled": enable_alerts, "sentiment_alerts": enable_sentiment_alerts}
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
    st.subheader("Send Test Email")
    if st.button("Send Test Email"):
        if not email:
            st.error("Please enter your email first.")
        else:
            st.info("Sending test email...")
            try:
                content, _ = generate_daily_summary()
                send_email(email, content)
                st.success(f"✅ Test email sent successfully to {email}!")
            except Exception as e:
                st.error(f"❌ Failed to send test email: {e}")