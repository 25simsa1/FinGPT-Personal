# FinGPT-Personal: Quantitative Portfolio Oversight & Risk Governance

## I. System Architecture and Design Philosophy
**FinGPT-Personal** is a modular computational framework designed for real-time portfolio valuation and autonomous risk mitigation. The system leverages Large Language Models (LLMs) to transform unstructured financial news into actionable sentiment data, bridging the gap between qualitative market narratives and quantitative portfolio management.

### Core Objectives
* **Dynamic Valuation:** Automated aggregation of multi-asset holdings with real-time P/L calculation.
* **Heuristic Risk Monitoring:** Deployment of sentiment-based triggers to identify bearish momentum in underlying equities.
* **Fault-Tolerant Deployment:** Optimized for cloud environments via explicit runtime configurations and comprehensive error handling.

---

## II. Repository Structure and Module Definitions

| File / Module | Functionality |
| :--- | :--- |
| **`app.py`** | Primary interface; handles HTML rendering and web-based visualization. |
| **`alerts.py`** | Asynchronous notification engine; interfaces with **Resend API** for stakeholder reporting. |
| **`summarizer.py`** | LLM integration layer; utilizes NLP to generate sentiment scores from raw news text. |
| **`data_fetcher.py`** | ETL pipeline; manages ingestion from market APIs and financial news aggregators. |
| **`portfolio.py`** | Core financial logic; executes capital allocation tracking and valuation metrics. |
| **`Procfile` / `runtime.txt`** | Deployment manifests ensuring environment parity across production servers. |

---

## III. Implementation of Automated Governance

The system implements a **Human-in-the-Loop (HITL)** governance model, particularly within the `monitor_sentiment` function. By mapping qualitative sentiment to a discrete numerical scale ($s \in \{-1, 0, 1\}$), the system enforces a deterministic threshold ($\tau$) for risk alerts.

The trigger logic is defined as:
$$\text{Alert Flagged if: } s_i \leq \tau$$

Where $s_i$ represents the sentiment score for a specific ticker $i$. This ensures that "High-Risk" market shifts are flagged for human oversight before significant capital erosion occurs.

---

## IV. Technical Sophistication & Version Control
The development lifecycle of this project prioritizes **System Stability** and **Data Integrity**:

* **Defensive Programming:** Recent iterations focused on `NoneType` error handling in the `summarizer` and `data_fetcher` modules to ensure UI/UX consistency.
* **Data Visualization:** Integration of `Plotly` within `requirements.txt` allows for interactive time-series analysis of portfolio performance and sentiment correlation.
* **Environment Integrity:** Strict utilization of `.gitignore` and `.env` files to maintain separation between sensitive API credentials (e.g., `RESEND_API_KEY`) and public source code.

---

## V. Dependencies and Environment
* **Language:** Python 3.x
* **Data Science:** `Pandas`, `NumPy`, `Plotly`
* **AI/ML:** `Transformers`, `FinGPT`
* **Operations:** `Resend`, `Dotenv`, `Flask`

---

**Author:** Simon Sang  
**Affiliation:** Colby College | Math & Economics
