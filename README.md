# RetailRadar
 
RetailRadar is a Streamlit dashboard for exploring a synthetic Sri Lankan retail transaction dataset, modeled on the UCI Online Retail dataset but localized to Sri Lanka — LKR pricing built on historically grounded exchange rates, districtwise geography, and demand patterns shaped by real events like COVID-19 and the 2022 economic crisis.
 
## Features
 
- **Bring your own data** — upload a CSV on the Welcome page, or explore the bundled demo dataset out of the box.
- **Sales Performance Analysis** — revenue broken down by year (donut chart), month, year × month, day of week, and hour, using a mix of Plotly, native Streamlit charts, and line charts.
- **Districtwise Distribution** — a choropleth map of Sri Lanka's districts paired with a matching ranked bar chart, sharing a single custom color palette for visual consistency.
## Project Structure
 
```
RetailRadar/
├── Application/
│   ├── .streamlit/
│   │   └── config.toml        # Streamlit theme configuration
│   ├── dashboard.py           # Entry point — wires up multi-page navigation
│   ├── welcome.py             # Landing page + CSV upload
│   ├── chart_page.py          # Sales Performance Analysis page
│   ├── heatmap_page.py        # Districtwise Distribution page (map + bar chart)
│   └── streamlitTests.py      # Scratch/dev file — not wired into navigation
├── data/
│   ├── input/                # Dataset(s) to be processed
│   ├── output/                # Processed dataset(s) consumed by the app
│   └── geodata/                # Sri Lanka district boundary GeoJSON
├── data_pipeline.py            # Cleans and processes the raw dataset
├── sri_lankanize_data.py       # Localizes a base retail dataset to Sri Lankan context
│                                 (LKR conversion, districts, COVID/crisis-era weighting)
├── notebook.ipynb              # Exploratory analysis / prototyping
├── requirements.txt
└── README.md
```
 
## Getting Started
 
### Prerequisites
- Python 3.9+
- pip
### Installation
```bash
git clone <your-repo-url>
cd RetailRadar
pip install -r requirements.txt
```
 
### Run the app
```bash
cd Application
streamlit run dashboard.py
```
 
## Data
 
The app expects a processed CSV under `data/output/` and a district-level boundary file at `data/geodata/District_geo.json`. If no file is uploaded via the Welcome page, it falls back to the bundled demo dataset.
 
Expected columns include: `InvoiceDate`, `CustomerID`, `Quantity`, `UnitPrice`, `Total_Price_LKR`, `District`.
 
Raw data is cleaned via `data_pipeline.py`, and `sri_lankanize_data.py` handles localizing a base retail dataset (currency conversion to LKR, district assignment, and economic-era weighting) before it's consumed by the dashboard.
 
## Tech Stack
 
- [Streamlit](https://streamlit.io/) — app framework & multi-page navigation
- [Pandas](https://pandas.pydata.org/) — data wrangling
- [GeoPandas](https://geopandas.org/) — choropleth geometry handling
- [Altair](https://altair-viz.github.io/) — bar chart with custom color scales
- [Plotly Express](https://plotly.com/python/plotly-express/) — donut chart
- [Matplotlib](https://matplotlib.org/) — choropleth rendering