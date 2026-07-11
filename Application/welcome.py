import streamlit as st
import pandas as pd

st.set_page_config(page_title="Welcome")
st.write("# Welcome to Retail Radar")
st.sidebar.success("*select a demo above.*")

st.markdown(
    """
*Upload dataset (.csv)*
"""
)

uploaded_file = st.file_uploader("Choose a file (.csv)", accept_multiple_files=False, type=".csv")

if uploaded_file:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe.head(10))