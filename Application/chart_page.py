import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Plotting Demo", page_icon="📈")

st.markdown("# Plotting Demo")
col1, col2 = st.columns(2, gap='xxlarge')

if "dataset" in st.session_state:
    df = st.session_state['dataset']
    st.sidebar.markdown("*Currently using uploaded file.*")
else:
    st.sidebar.markdown("*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*")
    df = pd.read_csv("../data/output/srilanka_retail_2020_2026_small.csv")

df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Year'] = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month

#Year vs total price charts
year_data = df.groupby('Year')['Total_Price_LKR'].sum().reset_index()
year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000
with col1:
    st.markdown("### Year vs Total Price ###")
    fig, ax = plt.subplots(figsize=(6, 6))

    explode = (0.05,)*(len(year_data))
    texts = ax.pie(
        year_data['Total_Price_LKR'],
        labels=year_data['Year'], 
        explode=explode,
        autopct='%1.1f%%',     # Formats percentage string format
        startangle=90,          # Rotates starting point 90 degrees counter-clockwise
        textprops={'fontsize': 12},
                colors=['#E6E6FF', '#B8B8FF','#8A8AFF', '#5C5CFF','#2E2EFF','#0000FF','#0000D1', '#0000A3','#000047']
    )[1]
    for text in texts:
        text.set_color('white') 
    # Get a doughnut shape
    # centre_circle = plt.Circle((0,0), 0.30, fc='white')
    # fig.gca().add_artist(centre_circle)
    ax.axis('equal')  
    st.pyplot(fig, transparent=True)

# Item vs quantity charts
with col2:
    st.markdown("### Item vs Quantity ###")
    Item_data = df.groupby('Description')['Quantity'].sum().reset_index()
    my_chart = st.bar_chart(Item_data, x='Description', y="Quantity", x_label='Item', y_label='Number of sold items')


# District vs Total price charts
with col1:
    st.markdown("### District vs Total price ###")
    district_data = df.groupby('District')['Total_Price_LKR'].sum().reset_index()
    district_data['Total_Price_LKR'] = district_data['Total_Price_LKR'] / 1000000

    my_chart = st.line_chart(district_data, x='District', y='Total_Price_LKR', x_label='District', y_label='Total Price in Million LKR')
