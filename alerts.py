# alerts.py (no attachment version)
import os
import resend
import traceback
from dotenv import load_dotenv
from portfolio import calculate_portfolio_value
from summarizer import analyze_sentiment

# --- Load environment ---
load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
if not RESEND_API_KEY:
    print("⚠️ Missing RESEND_API_KEY. Emails won't send.")
else:
    resend.api_key = RESEND_API_KEY


def generate_daily_summary():
    """Build portfolio summary text."""
    df, summary = calculate_portfolio_value()
    total_value = summary.get("Total Value ($)", 0)
    total_pnl = summary.get("Net P/L ($)", 0)

    message = f"""
FinGPT Daily Portfolio Summary



Portfolio Value: ${total_value:,.2f}
Net P/L: ${total_pnl:,.2f}

Holdings Summary:
{df.to_string(index=False)}

Sentiment Snapshot: {analyze_sentiment(str(df))}

Generated automatically by FinGPT.me
"""
    # Save portfolio to CSV for attachment
    df.to_csv("portfolio_report.csv", index=False)
    return message, "portfolio_report.csv"

import pandas as pd
from summarizer import analyze_sentiment, summarize_text
from data_fetcher import get_stock_data, get_extended_news

def monitor_sentiment(threshold=-0.5):
    """
    Monitors your portfolio sentiment and sends an alert if it turns bearish.
    """
    df, summary = calculate_portfolio_value()
    bearish_tickers = []

    for ticker in df["Ticker"]:
        try:
            data = get_stock_data(ticker)
            news = get_extended_news(ticker)
            news_text = "\n".join([n["title"] + ": " + n["summary"] for n in news])
            summary_text = summarize_text(ticker, data, news_text)
            sentiment = analyze_sentiment(summary_text)

            # Convert sentiment to numeric score
            score_map = {"positive": 1, "neutral": 0, "negative": -1}
            score = score_map.get(sentiment, 0)

            if score <= threshold:
                bearish_tickers.append((ticker, sentiment, summary_text))
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")

    if bearish_tickers:
        alert_message = "🚨 **Bearish Sentiment Detected**\n\n"
        for t, s, summary_text in bearish_tickers:
            alert_message += f"**{t}** — {s.upper()}\n{summary_text[:400]}...\n\n"
        send_email(os.getenv("ALERT_EMAIL"), alert_message)
        print("✅ Bearish sentiment alert sent!")
    else:
        print("No bearish sentiment detected.")

<<<<<<< HEAD

def send_email(recipient_email: str, content: str):
    """Send an email using Resend API (no attachment)."""
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY missing.")
        return None

    try:
        params = {
            "from": "FinGPT Alerts <alerts@fingpt.me>",
            "to": [recipient_email],
            "subject": "Your FinGPT Daily Summary",
            "text": content
        }

        response = resend.Emails.send(params)
        print(f"✅ Email sent successfully to {recipient_email}")
        return response

    except Exception as e:
        print(f"❌ Email send failed for {recipient_email}: {e}")
        print(traceback.format_exc())
        return None
=======
def send_email(recipient_email, content):
    import resend
    
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    if not resend.api_key:
        raise Exception("RESEND_API_KEY not set in environment variables")
    
    params = {
        "from": "FinGPT <onboarding@resend.dev>",
        "to": [recipient_email],
        "subject": "FinGPT Daily Summary",
        "text": content,
    }
    
    # Add attachment if exists
    if os.path.exists("portfolio_report.csv"):
        with open("portfolio_report.csv", "rb") as f:
            import base64
            content_base64 = base64.b64encode(f.read()).decode()
            params["attachments"] = [{
                "filename": "portfolio_report.csv",
                "content": content_base64
            }]
    
    response = resend.Emails.send(params)
    print(f"✅ Email sent to {recipient_email}, ID: {response['id']}")
    
def schedule_daily_alert(email):
    schedule.every().day.at("09:00").do(lambda: send_email(email, generate_daily_summary()))
    print(f"Scheduled daily FinGPT alerts for {email} at 09:00")
    while True:
        schedule.run_pending()
        time.sleep(60)

def schedule_daily_alert(email):
    schedule.every().day.at("09:00").do(lambda: send_email(email, generate_daily_summary()))
    print(f"Scheduled daily FinGPT alerts for {email} at 09:00")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    email = os.getenv("EMAIL_SENDER") or input("Enter your email: ")
    schedule_daily_alert(email)
    schedule.every().day.at("09:15").do(monitor_sentiment)

>>>>>>> c8587cdbf30a424787b25f5311353b6b3b998503
