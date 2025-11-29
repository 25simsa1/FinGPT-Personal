# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import json, os
from dotenv import load_dotenv
<<<<<<< HEAD

load_dotenv()

=======
>>>>>>> c8587cdbf30a424787b25f5311353b6b3b998503
from supabase import create_client, Client
from data_fetcher import get_stock_data, get_extended_news
from summarizer import summarize_text, analyze_sentiment
from portfolio import add_holding, remove_holding, calculate_portfolio_value
from alerts import send_email, generate_daily_summary

<<<<<<< HEAD
# --- Setup ---
st.set_page_config(page_title="FinGPT-Personal", layout="wide")

# Correct Supabase environment variable usage
=======
# --- Load environment variables ---
load_dotenv()

# --- Setup ---
st.set_page_config(page_title="FinGPT-Personal", layout="wide")

# ✅ Correct Supabase environment variable usage
>>>>>>> c8587cdbf30a424787b25f5311353b6b3b998503
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("⚠️ Supabase credentials missing. Please set SUPABASE_URL and SUPABASE_KEY in your environment.")
    supabase = None  # Set to None so the rest of the code doesn't crash
<<<<<<< HEAD

=======
    
>>>>>>> c8587cdbf30a424787b25f5311353b6b3b998503
# --- Custom styling ---
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
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    st.header("AI Equity Research Copilot")

    ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", "AAPL").upper()

    # Time range selector
    period = st.selectbox(
        "Select Price History Range",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"],
        index=2
    )

    st.markdown("**Indicators**")
    col_ind1, col_ind2, col_ind3 = st.columns(3)
    with col_ind1:
        show_ma = st.checkbox("Moving Averages (50 & 200)", value=True)
    with col_ind2:
        show_rsi = st.checkbox("RSI (14)", value=True)
    with col_ind3:
        show_macd = st.checkbox("MACD (12, 26, 9)", value=True)

    if st.button("Analyze"):
        with st.spinner('Fetching market data...'):
            data = get_stock_data(ticker)

        with st.spinner(f'Fetching {period} price history...'):
            hist = yf.download(ticker, period=period, progress=False)

        if hist.empty:
            st.warning("No historical data found for this ticker / period.")
            st.stop()

        with st.spinner('Fetching news...'):
            news_items = get_extended_news(ticker)

        with st.spinner('Generating summary...'):
            news_text = "\n".join([n['title'] + ': ' + n['summary'] for n in news_items])
            summary = summarize_text(ticker, data, news_text)
            sentiment = analyze_sentiment(summary)

        st.subheader(f"Fundamentals for {ticker}")
        st.dataframe(pd.DataFrame([data]))

        # --- Price History with Indicators ---
        st.subheader(f"Price History ({period}) — Interactive Chart")

        # Moving Averages (only if enough data)
        if show_ma and len(hist) >= 50:
            hist["MA50"] = hist["Close"].rolling(window=50).mean()
        if show_ma and len(hist) >= 200:
            hist["MA200"] = hist["Close"].rolling(window=200).mean()

        # RSI Calculation (Wilder smoothing)
        delta = hist["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss
        hist["RSI"] = 100 - (100 / (1 + rs))

        # MACD Calculation
        fast_ema = hist["Close"].ewm(span=12, adjust=False).mean()
        slow_ema = hist["Close"].ewm(span=26, adjust=False).mean()
        hist["MACD"] = fast_ema - slow_ema
        hist["Signal"] = hist["MACD"].ewm(span=9, adjust=False).mean()
        hist["MACD_Hist"] = hist["MACD"] - hist["Signal"]

        # --- Build subplot layout dynamically based on selected indicators ---
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

        # Row indices
        price_row = 1
        volume_row = 2
        next_row = 3
        rsi_row = None
        macd_row = None
        if show_rsi:
            rsi_row = next_row
            next_row += 1
        if show_macd:
            macd_row = next_row

        # --- Candlestick chart ---
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Price',
            increasing_line_color="green",
            decreasing_line_color="red",
            showlegend=False
        ), row=price_row, col=1)

        # --- MA Lines ---
        if show_ma and "MA50" in hist and hist["MA50"].notna().any():
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["MA50"],
                line=dict(color="blue", width=1),
                name="MA50"
            ), row=price_row, col=1)

        if show_ma and "MA200" in hist and hist["MA200"].notna().any():
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["MA200"],
                line=dict(color="orange", width=1),
                name="MA200"
            ), row=price_row, col=1)

        # --- Volume (colored up/down) ---
        vol_colors = [
            "green" if c >= o else "red"
            for o, c in zip(hist["Open"], hist["Close"])
        ]

        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"],
            name="Volume",
            marker_color=vol_colors,
            showlegend=False
        ), row=volume_row, col=1)

        # --- RSI ---
        if show_rsi:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["RSI"],
                line=dict(color="purple", width=1.2),
                name="RSI (14)"
            ), row=rsi_row, col=1)

            fig.add_hline(
                y=70, line_dash="dash", line_color="red",
                row=rsi_row, col=1,
                annotation_text="Overbought", annotation_position="top left"
            )
            fig.add_hline(
                y=30, line_dash="dash", line_color="green",
                row=rsi_row, col=1,
                annotation_text="Oversold", annotation_position="bottom left"
            )
            fig.update_yaxes(range=[0, 100], row=rsi_row, col=1)

        # --- MACD ---
        if show_macd:
            # MACD line
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["MACD"],
                line=dict(color="blue", width=1),
                name="MACD"
            ), row=macd_row, col=1)

            # Signal line
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Signal"],
                line=dict(color="orange", width=1),
                name="Signal"
            ), row=macd_row, col=1)

            # MACD Histogram
            fig.add_trace(go.Bar(
                x=hist.index, y=hist["MACD_Hist"],
                name="MACD Hist",
                opacity=0.4
            ), row=macd_row, col=1)

        # Layout tweaks
        fig.update_layout(
            height=900,
            xaxis_rangeslider_visible=False,
            template="plotly_white",
            title=f"{ticker} — Price, Volume, RSI & MACD ({period})",
            margin=dict(l=40, r=20, t=60, b=40),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom", y=-0.25,
                xanchor="center", x=0.5
            )
        )

        # Make all x-axes show a vertical “crosshair” line
        fig.update_xaxes(
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            showline=True
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption("RSI > 70 = overbought, < 30 = oversold. MACD crossovers and histogram shifts indicate momentum changes.")

        # --- Recent News ---
        st.subheader("Recent News")
        for n in news_items:
            st.markdown(f"- [{n['title']}]({n['link']})")

        # --- AI Summary ---
        st.subheader("AI Summary")
        st.text(summary)

        # --- Sentiment Indicator ---
        st.subheader("Sentiment Indicator")
        if sentiment == "positive":
            st.success("📈 Bullish sentiment detected")
        elif sentiment == "negative":
            st.error("📉 Bearish sentiment detected")
        else:
            st.info("⚖️ Neutral sentiment detected")

        score_map = {"positive": 1, "neutral": 0, "negative": -1}
        score = score_map[sentiment]
        fig_sent, ax = plt.subplots(figsize=(4, 0.5))
        color = "green" if score > 0 else "red" if score < 0 else "gray"
        ax.barh(["Sentiment"], [score], color=color)
        ax.set_xlim(-1, 1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_frame_on(False)
        st.pyplot(fig_sent)

# ===== Daily Alerts Setup =====
elif section == "Daily Alerts Setup":
    st.header("Daily Alerts Setup")
    st.write("Set up automatic daily email summaries of your portfolio.")

    email = st.text_input("Enter your email address")

    enable_alerts = False
    enable_sentiment_alerts = False

    # Load settings from Supabase
    if SUPABASE_URL and SUPABASE_KEY and email:
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
    st.subheader("Send Test Email")
    if st.button("Send Test Email"):
        if not email:
            st.error("Please enter your email first.")
        else:
            st.info("Sending test email...")
            try:
                content = generate_daily_summary()
                send_email(email, content)
                st.success(f"✅ Test email sent successfully to {email}!")
            except Exception as e:
                st.error(f"❌ Failed to send test email: {e}")
