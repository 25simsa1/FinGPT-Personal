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
    return message

def send_email(recipient_email, content):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")


    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "FinGPT Daily Summary"
    msg.attach(MIMEText(content, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Daily summary email sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

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
