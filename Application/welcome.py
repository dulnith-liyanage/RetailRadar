import streamlit as st
import pandas as pd
from utils import get_raw_data, clean_data

st.set_page_config(page_title="Welcome")
st.write("# Welcome to Retail Radar")
st.sidebar.success("*select a demo above.*")

uploaded_file = st.file_uploader("Choose a file (.csv)", accept_multiple_files=False, type=".csv")

if uploaded_file:
    dataframe = pd.read_csv(uploaded_file)
    st.session_state["dataset"] = dataframe

    st.success("Dataset successfully uploaded and saved to memory!")

# --- Data Preview & Overview (reflects uploaded file, or demo data if none uploaded) ---
raw_df, is_uploaded = get_raw_data()
df = clean_data(raw_df)

st.markdown("### Data Overview")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("Total Transactions")
        st.markdown(f"## {df['InvoiceNo'].nunique():,}")

with col2:
    with st.container(border=True):
        st.markdown("Total Customers")
        st.markdown(f"## {df['CustomerID'].nunique():,}")

with col3:
    with st.container(border=True):
        st.markdown("Total Revenue (M LKR)")
        st.markdown(f"## {df['Total_Price_LKR'].sum() / 1_000_000:,.1f}")