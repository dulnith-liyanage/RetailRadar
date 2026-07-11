import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Sales Performance Analysis", page_icon="📈")

st.markdown("# Sales Performance Analysis")

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

## --- Feature Engineering ---
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"]
)

df["Year"] = df["InvoiceDate"].dt.year

df["Month"] = df["InvoiceDate"].dt.month

df["Month_Name"] = df["InvoiceDate"].dt.month_name()

df["Day"] = df["InvoiceDate"].dt.day_name()

df["Hour"] = df["InvoiceDate"].dt.hour

# Initialize columns for layout
col1, col2 = st.columns(2, gap='large')

# --- Total Revenue by Year ---
with col1:
    st.markdown("### Total Revenue by Year ###")

    # Total Revenue by Year
    year_data = df.groupby('Year')['Total_Price_LKR'].sum().reset_index()
    year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000
    
    total_revenue_value = year_data['Total_Price_LKR'].sum()

    total_text = f"{total_revenue_value:.1f} M LKR" 

    # Make sure Year is treated as discrete categories
    year_data['Year'] = year_data['Year'].astype(str)

    fig = px.pie(
        year_data, 
        names='Year', 
        values='Total_Price_LKR', 
        hole=0.7,  # Turns the pie chart into a donut
        # Matching the color palette sequence roughly to your current pastel colors:
        color_discrete_sequence=['#f3ded7', '#c29df1', '#ec8792', '#eed1a2', '#a2db9a', '#92d6e3', '#8db2f3'] 
    )

    # Style the central hole text, gaps between slices, and the horizontal legend
    fig.update_layout(
        annotations=[
            # Top line text inside hole
            dict(text='TOTAL REVENUE', x=0.5, y=0.54, font_size=13, showarrow=False, font_color="#a0aab8",),
            # Bottom main calculation text inside hole
            dict(text=total_text, x=0.5, y=0.49, font_size=20, showarrow=False, font_color="white")
        ],
        legend=dict(
            orientation="h",       # Makes the legend horizontal instead of vertical
            yanchor="bottom",
            y=-0.15,               # Positions legend neatly beneath the chart
            xanchor="center",
            x=0.5,
            title=None
        ),
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20)  # Adjust margins to reduce whitespace
    )

    # Hide the text percentages on the chart slices and add the clean white borders
    fig.update_traces(
        textinfo='none', 
        marker=dict(line=dict(color='#0e1117', width=4)) # Match this hex color to your dashboard background
    )

    st.plotly_chart(fig, use_container_width=True)
        

# --- Total Revenue by Month ---
with col2:
    st.markdown("### Total Revenue by Month ###")
    monthly_revenue_only = df.groupby('Month')['Total_Price_LKR'].sum().reset_index()
    monthly_revenue_only['Total_Price_LKR'] = monthly_revenue_only['Total_Price_LKR'] / 1000000

    st.bar_chart(monthly_revenue_only, x='Month', y='Total_Price_LKR',
                 y_label='Total Revenue in Million LKR', color="#f3ded7")


# --- Total Revenue by Year and Month ---
monthly_revenue = df.groupby(['Year', 'Month'])['Total_Price_LKR'].sum().reset_index()
monthly_revenue['Total_Price_LKR'] = monthly_revenue['Total_Price_LKR'] / 1000000

# Make sure Year is treated as discrete categories
monthly_revenue['Year'] = monthly_revenue['Year'].astype(str)

st.markdown("### Total Revenue by Year and Month ###")
year_chart = st.bar_chart(monthly_revenue, x='Month', y='Total_Price_LKR', 
                          color='Year', y_label='Total Revenue in Million LKR', stack=False)

# Initialize columns for layout
col3, col4 = st.columns(2, gap='large')

# --- Weekly Revenue Trend ---

with col3:
    st.markdown("### Weekly Revenue Trend ###")
    weekly_sales = df.groupby("Day")["Total_Price_LKR"].sum().reset_index()

    weekly_sales["Total_Price_LKR"] = weekly_sales["Total_Price_LKR"] / 1000000  # Convert to millions

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    weekly_sales['Day'] = pd.Categorical(weekly_sales['Day'], categories=day_order, ordered=True)

    weekly_sales = weekly_sales.sort_values('Day')


    st.line_chart(weekly_sales, x="Day", y="Total_Price_LKR", y_label="Total Revenue in Million LKR"
                  ,color="#8aadf4")

# --- Hourly Revenue Trend ---
with col4:
    st.markdown("### Hourly Revenue Trend ###")
    hourly_sales = df.groupby('Hour')['Total_Price_LKR'].sum().reset_index()
    hourly_sales['Total_Price_LKR'] = hourly_sales['Total_Price_LKR'] / 1000000  # Convert to millions

    st.line_chart(hourly_sales, x='Hour', y='Total_Price_LKR', y_label='Total Revenue in Million LKR'
                  ,color="#8aadf4")