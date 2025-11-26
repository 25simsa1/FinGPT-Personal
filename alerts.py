# alerts.py
import time
import schedule 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from portfolio import calculate_portfolio_value
from summarizer import analyze_sentiment
import os
from dotenv import load_dotenv
load_dotenv()


def generate_daily_summary():
    df, summary = calculate_portfolio_value()
    total_value = summary['Total Value ($)']
    total_pnl = summary['Net P/L ($)']
    message = f"""FinGPT Daily Summary



Portfolio Value: ${total_value:,.2f}
Net P/L: ${total_pnl:,.2f}

Holdings Summary:
{df.to_string(index=False)}

Sentiment: {analyze_sentiment(str(df))}
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


def send_email(recipient_email, content):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    # Debug: Check if credentials are loaded
    if not sender_email:
        raise Exception("❌ EMAIL_SENDER environment variable is not set")
    if not sender_password:
        raise Exception("❌ EMAIL_PASSWORD environment variable is not set")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "FinGPT Daily Summary"
    msg.attach(MIMEText(content, 'plain'))
    
    # Attach portfolio report if provided
    if os.path.exists("portfolio_report.csv"):
        with open("portfolio_report.csv", "rb") as f:
            from email.mime.base import MIMEBase
            from email import encoders
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename="portfolio_report.csv")
            msg.attach(part)
    
    # Remove try-except to see the real error
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print(f"✅ Daily summary email sent to {recipient_email}")

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

