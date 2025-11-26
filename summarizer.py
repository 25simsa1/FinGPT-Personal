import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_text(ticker: str, fundamentals: dict, news: list):
    """Generate a research-style summary combining quantitative and qualitative data."""
    # Build the context string from fundamentals
    fundamentals_text = "\n".join([f"{k}: {v}" for k, v in fundamentals.items() if v])
    news_text = "\n".join([f"- {n['title']}: {n['summary']}" for n in news]) if news else "No recent news found."

    prompt = f"""
You are a senior equity research analyst. Write a clear, professional, one-paragraph summary of {ticker}.
Use the fundamentals and recent news provided below. Include trends, profitability, valuation, and sentiment.

### Fundamentals:
{fundamentals_text}

### News Headlines:
{news_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-5.1-chat-latest",
            messages=[
                {"role": "system", "content": "You are a CFA-level finance analyst writing investor insights."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Fallback) Could not connect to LLM: {e}"
