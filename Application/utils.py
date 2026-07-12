import streamlit as st
import pandas as pd

def get_raw_data():
    if "dataset" in st.session_state:
        return st.session_state["dataset"], True
    return pd.read_csv("../data/output/srilanka_retail_2020_2026.csv"), False

@st.cache_data
def clean_data(df):
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.month
    df["Month_Name"] = df["InvoiceDate"].dt.month_name()
    df["Day"] = df["InvoiceDate"].dt.day_name()
    df["Hour"] = df["InvoiceDate"].dt.hour

    return df