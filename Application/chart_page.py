import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Plotting Demo", page_icon="📈")

st.markdown("* Plotting Demo")
col1, col2 = st.columns(2, gap='xxlarge')

if "dataset" in st.session_state:
    df = st.session_state['dataset']
    st.sidebar.markdown("*Currently using uploaded file.*")
else:
    st.sidebar.markdown("*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*")
    df = pd.read_csv("../data/output/srilanka_retail_2020_2026_small.csv")

# Remove rows with missing CustomerID values
df = df.dropna(
    subset=["CustomerID"]
)

# Convert CustomerID to integer type
df["CustomerID"] = df["CustomerID"].astype(int)

# Remove rows with non-positive Quantity values
df = df[
    df["Quantity"] > 0
]

# Remove rows with zero UnitPrice values
df = df[
    df["UnitPrice"] > 0
]

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"]
)

df["Year"] = df["InvoiceDate"].dt.year

df["Month"] = df["InvoiceDate"].dt.month

df["Month_Name"] = df["InvoiceDate"].dt.month_name()

df["Day"] = df["InvoiceDate"].dt.day_name()

df["Hour"] = df["InvoiceDate"].dt.hour


#Year vs total price charts
year_data = df.groupby('Year')['Total_Price_LKR'].sum().reset_index()
year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000

with col1:
    st.markdown("Distribution of total price by year")
    fig, ax = plt.subplots(figsize=(6, 6))

    year_price = list(year_data["Total_Price_LKR"])
    smallest = year_price.index(min(year_price))
    
    explode = [0]*(len(year_data))
    explode[smallest] = 0.1

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
    st.markdown("Top 20 Products by sold quantity")
    top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(20).reset_index()
    top_products = top_products[::-1].reset_index(drop=True)
    my_chart = st.bar_chart(top_products, x='Description', y="Quantity", x_label='Product', y_label='Number of sold items', color='#264653')


# District vs Total price charts
with col1:
    st.markdown("District vs Total price ")
    
    district_data = df.groupby('District')['Total_Price_LKR'].sum().reset_index()
    district_data['Total_Price_LKR'] = district_data['Total_Price_LKR'] / 1000000

    my_chart = st.line_chart(district_data, x='District', y='Total_Price_LKR', x_label='District', y_label='Total Price in Million LKR')

with col2:
    st.markdown("Monthly revenue over years")
    monthly_revenue = df.groupby(['Year', 'Month'])['Total_Price_LKR'].sum().reset_index()
    monthly_revenue['Total_Price_LKR'] = monthly_revenue['Total_Price_LKR'] / 1000000

    my_chart = st.bar_chart(monthly_revenue, x='Month', y='Total_Price_LKR', color='Year',horizontal=True)

with col1:
    st.markdown("Total revenue by month")
    monthly_revenue_only = df.groupby('Month')['Total_Price_LKR'].sum().reset_index()
    monthly_revenue_only['Total_Price_LKR'] = monthly_revenue_only['Total_Price_LKR'] / 1000000
    my_chart = st.bar_chart(monthly_revenue, x='Month', y='Total_Price_LKR', color='#30827f', x_label='Month',
                            y_label='Total Price in Million LKR')

with col2:
    st.markdown("Total Sales by Day of the Week")
    daily_sales = df.groupby('Day')["Total_Price_LKR"].sum().reset_index()

    daily_sales["Total_Price_LKR"] = daily_sales["Total_Price_LKR"] / 1000000  # Convert to millions
    my_chart = st.bar_chart(daily_sales, x='Day', y='Total_Price_LKR', color='#8ec456', x_label='Day',
                            y_label='Total Price in Million LKR')

with col1:
    st.markdown("Hourly Trends")
    hourly_sales = df.groupby('Hour')['Total_Price_LKR'].sum().reset_index()
    hourly_sales['Total_Price_LKR'] = hourly_sales['Total_Price_LKR'] / 1000000  # Convert to millions
    my_chart = st.line_chart(hourly_sales, x='Hour', y='Total_Price_LKR', x_label='Hour of the Day', y_label='Total Price in Million LKR', color="#6553c0")

with col2:
    st.markdown("Top 20 Products by revenue")
    top_products = df.groupby('Description')['Total_Price_LKR'].sum().sort_values(ascending=False).head(20).reset_index()
    top_products = top_products[::-1].reset_index(drop=True)
    my_chart = st.bar_chart(top_products, x='Description', y="Total_Price_LKR", x_label='Product', y_label='Number of sold items', color="#4FB7E0")

with col1:
    st.markdown("Top 20 Customers")
    customer_data = df.groupby('CustomerID')['Total_Price_LKR'].sum().reset_index()
    top_customers = customer_data.sort_values(by='Total_Price_LKR', ascending=False).head(20)
    top_customers['Total_Price_LKR'] = top_customers['Total_Price_LKR'] / 1000000
    my_chart = st.bar_chart(top_customers, x='CustomerID', y="Total_Price_LKR", x_label='CustomerID', y_label='Total Price in Million LKR', color='#44a778')
