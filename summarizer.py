# summarizer.py
import os
from openai import OpenAI
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_text(ticker, fundamentals, news_text):
    """
    Generate an AI summary for a given stock.
    Combines fundamentals + latest news context.
    """
    fundamentals_text = "\n".join([f"{k}: {v}" for k, v in fundamentals.items()])
    prompt = f"""
    You are a financial research assistant.
    Summarize the current situation for {ticker}, combining:
    - Fundamental data
    - Recent news

    Focus on sentiment, valuation, and outlook.
    Keep it under 200 words.
    
    FUNDAMENTALS:
    {fundamentals_text}

    NEWS:
    {news_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # light & fast model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Fallback Summary) Could not generate AI summary: {e}"


def analyze_sentiment(text):
    """
    Simple sentiment analysis using TextBlob.
    Returns: 'positive', 'neutral', or 'negative'
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"