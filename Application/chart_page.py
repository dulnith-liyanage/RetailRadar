import streamlit as st
import pandas as pd

st.set_page_config(page_title="Plotting Demo", page_icon="📈")

st.markdown("# Plotting Demo")
st.sidebar.header("Plotting Demo")
chartType = st.selectbox("Chart type", ["Line chart", "Bar chart"])

st.write(
    """
"""
)

progress_bar = st.sidebar.progress(0)

df = pd.read_csv("D:\IBM-Datascientist\Python\RetailRadar\data\output\srilanka_retail_2020_2026.csv")
print(df.head)
year_data = df.groupby('InvoiceDate')['Total_Price_LKR'].sum().reset_index()
year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000
year_data['InvoiceDate'] =  year_data['InvoiceDate'][0][:4]
year_data = year_data.rename(columns={'InvoiceDate': 'Year'})

if chartType == "Bar chart":
    # year_data.plot(x='Year', y='Total_Price_LKR', kind='bar', title='Earnings in Million LKR by Year', xlabel='Year', ylabel='Total Price in Million LKR', legend=None, color='green', figsize=(8, 6))
    my_chart = st.bar_chart(year_data, x='Year', y="Total_Price_LKR", x_label='Year', y_label='Total Price in Million LKR')
if chartType == "Line chart":
    my_chart = st.line_chart(year_data, x='Year', y='Total_Price_LKR', x_label='Year', y_label='Total Price in Million LKR')

status_text = st.sidebar.empty()
progress_bar.empty()
