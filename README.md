# 🛍️ Retail Radar

A data science project that processes a real world e-commerce transactional dataset
to segment and analyze online retail customer behavior: purchasing recency, transaction 
frequency, monetary value, and targeted buyer personas, with an unsupervised K-means clustering model
and an interactive Streamlit dashboard.

---

## 1. Project structure

```
drone_delivery_project/
├── data_pipeline.py      # ETL + feature engineering + model training
├── dashboard.py           # Streamlit app (map, KPIs, charts, predictor)
├── sri_lankanize_data.py # Convert general data obtained from Kaggle to fit Sri Lankan standards
├── requirements.txt
├── online_retail.csv
├── online_retail_lk.csv
└── README.md
```

## 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Run the pipeline

```bash
python data_pipeline.py
```
