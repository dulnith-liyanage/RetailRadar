import streamlit as st
import pandas as pd
import welcome
import matplotlib.pyplot as plt

st.set_page_config(page_title="Plotting Demo", page_icon="📈")

st.markdown("# Plotting Demo")
st.sidebar.header("Plotting Demo")
chartType = st.selectbox("Chart type", ["Line chart", "Bar chart", "Pie chart"])

st.write(
    """
"""
)

if welcome.uploaded_file:
    st.write(welcome.uploaded_file)
    df = pd.read_csv(welcome.uploaded_file)
    st.markdown("*Currently using uploaded file.*")
else:
    st.write(welcome.uploaded_file)
    st.markdown("*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*")

df = pd.read_csv("../data/output/srilanka_retail_2020_2026.csv")
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Year'] = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month

#Year vs total price charts
st.markdown("## Year vs Total Price ##")
year_data = df.groupby('Year')['Total_Price_LKR'].sum().reset_index()
year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000
# year_data.plot(x='Year', y='Total_Price_LKR', kind='bar', title='Earnings in Million LKR by Year', xlabel='Year', ylabel='Total Price in Million LKR', legend=None, color='green', figsize=(8, 6))

if chartType == "Bar chart":
    # year_data.plot(x='Year', y='Total_Price_LKR', kind='bar', title='Earnings in Million LKR by Year', xlabel='Year', ylabel='Total Price in Million LKR', legend=None, color='green', figsize=(8, 6))
    my_chart = st.bar_chart(year_data, x='Year', y="Total_Price_LKR", x_label='Year', y_label='Total Price in Million LKR')
elif chartType == "Line chart":
    my_chart = st.line_chart(year_data, x='Year', y='Total_Price_LKR', x_label='Year', y_label='Total Price in Million LKR')
elif chartType == "Pie chart":
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
st.markdown("## Item vs Quantity ##")
Item_data = df.groupby('Description')['Quantity'].sum().reset_index()
# year_data.plot(x='Description', y='Quantity', kind='bar', title='Earnings in Million LKR by Year', xlabel='Year', ylabel='Total Price in Million LKR', legend=None, color='green', figsize=(8, 6))

if chartType == "Bar chart":
    my_chart = st.bar_chart(Item_data, x='Description', y="Quantity", x_label='Item', y_label='Number of sold items')
elif chartType == "Line chart":
    my_chart = st.line_chart(Item_data, x='Description', y='Quantity', x_label='Item', y_label='Number of sold items')
elif chartType == "Pie chart":
    st.markdown("*This item couldnt show as a pie chart*")
    my_chart = st.line_chart(Item_data, x='Description', y='Quantity', x_label='Item', y_label='Number of sold items')


# District vs Total price charts
st.markdown("## District vs Total price ##")
district_data = df.groupby('District')['Total_Price_LKR'].sum().reset_index()
district_data['Total_Price_LKR'] = district_data['Total_Price_LKR'] / 1000000

if chartType == "Bar chart":
    my_chart = st.bar_chart(district_data, x='District', y="Total_Price_LKR", x_label='District', y_label='Total Price in Million LKR')
elif chartType == "Line chart":
    my_chart = st.line_chart(district_data, x='District', y='Total_Price_LKR', x_label='District', y_label='Total Price in Million LKR')
elif chartType == "Pie chart":
    fig, ax = plt.subplots(figsize=(6, 6))

    explode = (0.01,)*(len(district_data))
    texts = ax.pie(
        district_data['Total_Price_LKR'],
        labels=district_data['District'], 
        explode=explode,
        colors=['#E6E6FF', '#B8B8FF','#8A8AFF', '#5C5CFF','#2E2EFF','#0000FF','#0000D1', '#0000A3','#000047'],
        startangle=90,          # Rotates starting point 90 degrees counter-clockwise
        textprops={'fontsize': 12}
    )[1]
    for text in texts:
        text.set_color('white')
    # Get a doughnut shape
    # centre_circle = plt.Circle((0,0), 0.30, fc='white')
    # fig.gca().add_artist(centre_circle)
    ax.axis('equal')  
    st.pyplot(fig, transparent=True)