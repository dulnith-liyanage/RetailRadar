# Retail Radar

**AI-powered retail analytics dashboard for the Sri Lankan retail sector.**

Retail Radar turns raw retail transaction data into revenue trends, district-wise performance maps, AI-driven customer segmentation, sales forecasting, and an in-app conversational analyst — all in a single multi-page Streamlit dashboard.

Built for **Data Odyssey 2026**, AI and Data Science Club, General Sir John Kotelawala Defence University.

---

## Features

| Page | What it does |
|---|---|
| **Welcome** | Landing page; lets you upload your own retail CSV or use the built-in demo dataset |
| **Sales Performance** 📈 | Revenue by year, month, week, and hour; year-over-year and month-over-month comparisons; revenue heatmaps; top products by revenue and quantity; annual sales forecast |
| **Districtwise Distribution** 📌 | Choropleth map of revenue by Sri Lankan district, paired with a ranked bar chart |
| **Customer Segments** 👥 | RFM (Recency, Frequency, Monetary) analysis with K-Means clustering to automatically group customers into behavioral segments, including spend-based insights and segment definitions |
| **Insight.AI** 🤖 | A chatbot grounded in the dashboard's own statistics, correlation matrix, product performance, customer segments, and sales forecast, powered by Groq |

---

## Tech Stack

- **Framework:** [Streamlit](https://streamlit.io/) (multi-page app via `st.navigation`)
- **Data processing:** pandas
- **Visualization:** Plotly Express, Altair, `st.bar_chart` / `st.line_chart`, Matplotlib
- **Geospatial:** GeoPandas
- **Machine learning:** scikit-learn (`StandardScaler`, `KMeans`, forecasting model)
- **LLM chatbot:** [Groq](https://groq.com/) API (`llama-3.3-70b-versatile`)

---

## Project Structure

```
Application/
├── dashboard.py              # Entry point — defines app navigation across pages
├── welcome.py                # Landing page / file upload
├── sales_performance.py      # Revenue trends, charts, and forecast
├── district_distribution.py  # Choropleth + district revenue ranking
├── rfm.py                    # RFM analysis, K-Means clustering, customer segments
├── bot.py                    # Insight.AI chatbot (Groq-powered)
├── TelegramBot.py            # Telegram chatbot integration
└── utils.py                   # Shared data loading, cleaning, segmentation, and forecasting functions

data/
├── datasets/
│   ├── sri_lanka_1.csv       # Sample retail dataset
│   └── sri_lanka_2.csv       # Sample retail dataset
├── output/
│   ├── srilanka_retail_2020_2026.csv         # Full demo dataset
│   └── srilanka_retail_2020_2026_small.csv   # Sampled dataset (used as chatbot context)
└── geodata/
    └── District_geo.json     # Sri Lanka district boundaries (GeoJSON)
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- A [Groq API key](https://console.groq.com/) for the Insight.AI chatbot
- A Telegram bot token if you plan to use the Telegram chatbot

### Installation

```bash
git clone <repository-url>
cd <repository-folder>
pip install -r requirements.txt
```

**Key dependencies** (add to `requirements.txt` if not already present):
```
streamlit
pandas
plotly
altair
geopandas
matplotlib
scikit-learn
groq
```

### Configuration

Insight.AI requires a Groq API key. Create `Application/.streamlit/secrets.toml`:

```toml
API_KEY = "your-groq-api-key-here"
```

If you are using the Telegram bot, also add your bot token:

```toml
TELE_BOT_API = "your-telegram-bot-token-here"
```

### Data

Expected columns in the retail dataset include (at minimum):
`CustomerID`, `InvoiceNo`, `InvoiceDate`, `Description`, `Quantity`, `UnitPrice`, `Total_Price_LKR`, `District`

### Run the app

```bash
cd Application
streamlit run dashboard.py
```

The app will open in your browser, defaulting to the **Welcome** page. From the sidebar, upload your own CSV or continue with the demo dataset — every other page (Sales Performance, Districtwise Distribution, Customer Segments, Insight.AI) will automatically reflect whichever dataset is active.

---

## How It Works

1. **Upload or use demo data** — `utils.get_raw_data()` checks session state for an uploaded file, falling back to the bundled demo CSV.
2. **Clean & process** — `utils.clean_data()` drops missing customer IDs, filters invalid quantities/prices, and derives Year, Month, Day, and Hour fields from the invoice date.
3. **Visualize** — Each page aggregates the cleaned data into the metrics and charts relevant to it, including revenue trends, district totals, product performance, and forecast charts.
4. **Segment customers** — `rfm.py` computes Recency, Frequency, and Monetary scores per customer, scales them, and runs K-Means clustering to assign each customer to a named behavioral segment.
5. **Forecast sales** — `utils.get_sales_forecast()` trains a monthly forecast model and shares the next 12 months of projected revenue across the dashboard and chatbot.
6. **Ask Insight.AI** — `bot.py` pre-computes summary statistics and feeds them into a system prompt for the Groq LLM, so the chatbot's answers are grounded in the same numbers shown elsewhere in the app.

---

## Competition Context

This project was developed for **Data Odyssey 2026**, organized by the AI and Data Science Club at General Sir John Kotelawala Defence University, under the theme *"Humanity x AI: The New Age of Innovation"*.

---
