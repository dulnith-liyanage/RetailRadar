# Retail Radar

**AI-powered retail analytics dashboard for the Sri Lankan retail sector.**

Retail Radar turns raw retail transaction data into revenue trends, regional performance maps, AI-driven customer segmentation, and an in-app conversational analyst — all in a single multi-page Streamlit app.

Built for **Data Odyssey 2026**, AI and Data Science Club, General Sir John Kotelawala Defence University.

---

## Features

| Page | What it does |
|---|---|
| **Welcome** | Landing page; lets you upload your own retail CSV or use the built-in demo dataset |
| **Sales Performance** 📈 | Revenue by year, month, and year-over-year comparison; weekly and hourly revenue trends; top 10 products by revenue and by quantity sold |
| **Districtwise Distribution** 📌 | Choropleth map of revenue by Sri Lankan district, paired with a ranked bar chart |
| **Customer Segments** 👥 | RFM (Recency, Frequency, Monetary) analysis with K-Means clustering to automatically group customers into behavioral segments (e.g. Champions, At-Risk VIPs, Lost Accounts); top 10 customers by spend; full segment definition table |
| **Insight.AI** 🤖 | A chatbot grounded in the dashboard's own statistics (descriptive stats, correlation matrix, revenue breakdowns) that answers business questions in plain language, powered by Groq |

---

## Tech Stack

- **Framework:** [Streamlit](https://streamlit.io/) (multi-page app via `st.navigation`)
- **Data processing:** pandas
- **Visualization:** Plotly Express, Altair, `st.bar_chart` / `st.line_chart`, Matplotlib (choropleth)
- **Geospatial:** GeoPandas
- **Machine learning:** scikit-learn (`StandardScaler`, `KMeans`)
- **LLM chatbot:** [Groq](https://groq.com/) API (`llama-3.3-70b-versatile`)

---

## Project Structure

```
Application/
├── dashboard.py              # Entry point — defines app navigation across all pages
├── welcome.py                 # Landing page / file upload
├── sales_performance.py       # Revenue trend charts
├── district_distribution.py   # Choropleth + district revenue ranking
├── rfm.py                     # RFM analysis, K-Means clustering, customer segments
├── bot.py                     # Insight.AI chatbot (Groq-powered)
└── utils.py                   # Shared data loading & cleaning functions

data/
├── output/
│   ├── srilanka_retail_2020_2026.csv         # Full demo dataset
│   └── srilanka_retail_2020_2026_small.csv   # Sampled dataset (used as chatbot context)
└── geodata/
    └── District_geo.json      # Sri Lanka district boundaries (GeoJSON)
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- A [Groq API key](https://console.groq.com/) for the Insight.AI chatbot

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
3. **Visualize** — Each page aggregates the cleaned data into the metrics and charts relevant to it (revenue trends, district totals, RFM scores).
4. **Segment customers** — `rfm.py` computes Recency, Frequency, and Monetary scores per customer, scales them, and runs K-Means (6 clusters) to assign each customer to a named behavioral segment.
5. **Ask Insight.AI** — `bot.py` pre-computes summary statistics and feeds them into a system prompt for the Groq LLM, so the chatbot's answers are grounded in the same numbers shown elsewhere in the app.

---

## Competition Context

This project was developed for **Data Odyssey 2026**, organized by the AI and Data Science Club at General Sir John Kotelawala Defence University, under the theme *"Humanity x AI: The New Age of Innovation."*

---