# FinGPT-Personal

A personal finance copilot that tracks my portfolio, reads the news for each holding, scores how positive or negative that news is, and emails me when something turns bearish enough to be worth a look.

It is a tool I run on my own holdings. It flags things for me to decide on. It does not trade, and it is not built for anyone else's money.

---

## Why I built it

During market hours I had a habit that ate my afternoons. I would check prices, then go read the news to figure out whether a dip was just noise or the start of something real, and I would do that one stock at a time until the whole day was gone.

The gathering was the boring part. The deciding was the part I actually cared about. So I wrote something to do the gathering for me: pull the prices, pull the news, tell me where the mood has shifted, and let me spend my attention on the call instead of the legwork.

---

## What it does

- Tracks a multi-asset portfolio and calculates live profit and loss
- Pulls recent financial news for each position I hold
- Runs that news through a language model to produce a sentiment score per ticker
- Compares each score against a threshold I set
- Emails me an alert (through the Resend API) when a holding crosses into bearish territory, so I can decide whether to act

The design choice underneath all of this is that a human stays in the loop. The tool's job is to make sure I see the right thing at the right time. The decision is always mine.

---

## How it works

The flow is a straight pipeline, and each file owns one step of it.

**1. Fetch.** `data_fetcher.py` pulls two kinds of data: market prices for the portfolio and recent news articles for each ticker. This is the messiest part of the system, because external feeds return incomplete or malformed data constantly, so a lot of the defensive code lives here.

**2. Score.** `summarizer.py` takes the raw news text and sends it to a language model, which returns a sentiment reading for each ticker. The reading is collapsed to a simple scale (negative, neutral, positive) so the rest of the system can reason about it numerically instead of wrestling with free text.

**3. Decide.** The monitoring logic compares each ticker's score against a threshold I configure. If a score lands at or below the threshold, that ticker gets flagged. The threshold is deliberately a knob I control, because how cautious I want to be changes with the market.

**4. Alert.** `alerts.py` takes the flagged tickers and sends me an email through Resend, so the signal reaches me whether or not I happen to have the dashboard open.

**5. Display.** `app.py` renders the dashboard: current holdings, profit and loss, and the sentiment picture, with Plotly charts for anything worth seeing over time.

One thing I want to be honest about in the design: a sentiment score is a proxy. It stands in for "is something happening with this stock," and like any proxy it can be tripped by noise. I learned this the hard way watching the threshold fire on nothing during a quiet week. That is exactly why a person makes the final call instead of the number doing it automatically.

---

## Project structure

| File | What it does |
| --- | --- |
| `app.py` | The dashboard and interface |
| `data_fetcher.py` | Pulls market prices and news from external APIs |
| `summarizer.py` | Sends news text to the language model and returns sentiment scores |
| `portfolio.py` | Holdings tracking, allocation, and profit-and-loss math |
| `alerts.py` | Builds and sends email alerts through Resend |
| `settings.json` | User configuration (holdings, thresholds, preferences) |
| `test_email.py` | A standalone check that the email pipeline works end to end |
| `requirements.txt` | Python dependencies |
| `Procfile`, `runtime.txt` | Deployment configuration |

---

## Stack

- **Language:** Python 3
- **Web framework:** [Flask or Streamlit -- set this to whatever app.py actually imports]
- **Data:** Pandas, NumPy
- **Charts:** Plotly
- **AI / NLP:** Hugging Face Transformers
- **Email:** Resend
- **Config / secrets:** python-dotenv

---

## Getting it running

Clone and install:

```bash
git clone https://github.com/25simsa1/FinGPT-Personal.git
cd FinGPT-Personal
pip install -r requirements.txt
```

Create a `.env` file in the project root with your keys. The app reads these at startup:

```
RESEND_API_KEY=your_resend_key
# [add any market-data or news API keys your data_fetcher.py uses]
```

Set your holdings and threshold in `settings.json`:

```json
{
  "holdings": ["TICKER1", "TICKER2"],
  "sentiment_threshold": [your value],
  "alert_email": "you@example.com"
}
```

(Adjust the keys above to match what your `settings.json` actually expects.)

Run it:

```bash
[your run command, e.g. "streamlit run app.py" or "python app.py"]
```

---

## Testing the email pipeline

Email is the one part that fails silently if a key is wrong, so there's a dedicated check for it:

```bash
python test_email.py
```

If you get the test message in your inbox, the Resend setup is good. If you don't, check that `RESEND_API_KEY` is set and that the from-address is verified on your Resend account.

---

## Deployment

The repo includes a `Procfile` and `runtime.txt`, so it deploys to a standard cloud host that reads those (Heroku-style). Set the same environment variables (`RESEND_API_KEY` and any data keys) in your host's config rather than committing a `.env` file. The `.gitignore` is set up to keep `.env` out of version control, which is where secrets should stay.

---

## What was hard, and what it taught me

The model was the easy part. Keeping the thing alive on real-world data was not.

News and market feeds return broken or missing fields all the time, and early versions of the app would crash mid-update on a single null value. A good chunk of the commit history is me learning to write code that handles bad input gracefully instead of falling over, which turned out to teach me more than the AI piece did.

The second lesson was about measurement. Building the threshold logic forced me to confront how easily a single number can pretend to be the truth. Once your alert depends on a proxy, the proxy is what you end up tuning, and you have to stay honest about the gap between the signal and the thing the signal is supposed to mean.

---

## Limitations

- Sentiment is a proxy and can fire on noise. The human-in-the-loop design is a direct response to that, not a footnote.
- It depends on external APIs, so its data is only as good and as current as those feeds.
- It is built and tuned for one user (me). It is not multi-tenant and not hardened for other people's accounts.

---

## Possible next steps

- Track alert accuracy over time so I can see how often a flag actually preceded a real move
- Let the threshold adapt per ticker instead of using one global value
- Add a short LLM-written rationale to each alert so the email explains *why* it fired, not just that it did

---

## Disclaimer

This is a personal project. It is not financial advice, and nothing it produces should be treated as a recommendation. I run it on my own holdings and at my own risk.

---

**Author:** Simon Sang -- Math & Economics, Colby College
