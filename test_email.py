from alerts import send_email, generate_daily_summary

# Replace with your own email (the one you want to receive the test)
recipient = "simonlapsang@gmail.com"

# Generate a short test message
content = "✅ FinGPT Email Test Successful! Your email configuration works."

# Try sending the email
send_email(recipient, content)
