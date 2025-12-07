# summarizer.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_text(ticker, fundamentals, news_text):
    """
    Generate a structured 3-paragraph equity summary:
    Overview
    Recent Developments
    Risks & Outlook
    """
    
    # Handle None or empty fundamentals
    if fundamentals and isinstance(fundamentals, dict) and len(fundamentals) > 0:
        fundamentals_text = "\n".join([f"{k}: {v}" for k, v in fundamentals.items()])
    else:
        fundamentals_text = "Fundamental data not available."

    prompt = f"""
You are a professional equity research analyst.

Write a concise, structured 3-paragraph summary of the stock **{ticker}** based on its fundamentals and recent market/news context.

---

### FUNDAMENTALS
{fundamentals_text}

### RECENT NEWS & MARKET EVENTS
{news_text[:2000] if news_text else "No recent news available."}

---

### OUTPUT INSTRUCTIONS
Write three clearly separated paragraphs (no bullet points):
1️⃣ **Overview** — Describe what the company does, its sector, valuation ratios, market position, and key financial highlights.
2️⃣ **Recent Developments** — Summarize at least two meaningful updates from the recent news or analyst commentary.
3️⃣ **Risks & Outlook** — Provide a brief risk analysis and investor outlook based on financial or macro trends.

Use a neutral, professional tone (similar to a Morningstar or Goldman Sachs summary).
Keep the response under 250 words.
Do NOT include section headers or markdown symbols — just clean paragraphs separated by a blank line.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.6,
        )
        summary = response.choices[0].message.content.strip()

        # Normalize paragraph spacing for UI formatting
        summary = "\n\n".join([p.strip() for p in summary.split("\n") if p.strip()])

        return summary

    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return "AI summary unavailable — check your OpenAI API key or network connection."


def analyze_sentiment(summary):
    """
    Simple rule-based sentiment analyzer using keywords from AI summary tone.
    """
    text = summary.lower()
    positive_keywords = ["growth", "strong", "beat", "bullish", "improved", "upside", "profit", "resilient", "momentum"]
    negative_keywords = ["decline", "weak", "bearish", "loss", "downgrade", "headwind", "slowdown", "risk"]

    if any(word in text for word in positive_keywords):
        return "positive"
    elif any(word in text for word in negative_keywords):
        return "negative"
    else:
        return "neutral"