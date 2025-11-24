import os
import textwrap
from openai import OpenAI
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_text(ticker: str, fundamentals: dict, news_text: str) -> str:
    prompt = f"""
    You are an equity research analyst. Given this data for {ticker}:
    Fundamentals: {fundamentals}
    News: {news_text}
    Provide a concise 5-sentence summary including valuation, momentum, and sentiment.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # Clean up weird spacing or newlines
        summary = response.choices[0].message.content
        summary = re.sub(r"\\s+", " ", summary).strip()
        return summary
    except Exception as e:
        return f"(Fallback) Could not connect to LLM: {e}\\nKey insights:\\n- P/E: {fundamentals.get('P/E Ratio')}\\n- Market Cap: {fundamentals.get('Market Cap')}\\n- EPS: {fundamentals.get('EPS')}"
    
from textblob import TextBlob

def analyze_sentiment(text: str) -> str:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"
