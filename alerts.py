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
    return message


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
