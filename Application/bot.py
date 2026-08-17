import streamlit as st
from groq import Groq
from utils import get_raw_data, clean_data, get_segment_summary, get_sales_forecast
import pandas as pd

st.set_page_config(page_title="Insight.AI")

# Initialize Groq Client
client = Groq(api_key=st.secrets['API_KEY'])

st.markdown(
    """
    <style>
    /* User Avatar: Nord11 (Red/Frost accent) */
    [data-testid="stChatMessageAvatarUser"] {
        background-color: #EBCB8B !important;
    }

    /* Assistant/Bot Avatar: Nord10 (Deep Blue) or Nord14 (Green) */
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #d08770 !important; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# DataFrame Integration
raw_df, is_uploaded = get_raw_data()
df = clean_data(raw_df)

# --- 1. PRE-SCHEDULED AGGREGATIONS & METRICS ---
describe = df.describe().to_markdown(index=True)

# Generate correlation matrix using only numeric columns
correlation = df.corr(numeric_only=True).to_markdown(index=True)

# Yearly Revenue (in Millions LKR)
year_data = df.groupby('Year')['Total_Price_LKR'].sum().reset_index()
year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000
year_data_md = year_data.to_markdown(index=False)

# Monthly Revenue (in Millions LKR)
monthly_revenue = df.groupby(['Year', 'Month'])['Total_Price_LKR'].sum().reset_index()
monthly_revenue['Total_Price_LKR'] = monthly_revenue['Total_Price_LKR'] / 1000000
monthly_revenue['Year'] = monthly_revenue['Year'].astype(str)
monthly_revenue_md = monthly_revenue.to_markdown(index=False)

# District-wise Revenue (in Hundred Thousands / Lakhs LKR)
districtwise_data = df.groupby(['District'])['Total_Price_LKR'].sum().reset_index()
districtwise_data['Total_Price_LKR'] = districtwise_data['Total_Price_LKR'] / 100000
districtwise_data_md = districtwise_data.to_markdown(index=False)

# --- NEW: Product Performance ---
product_revenue = df.groupby('Description')['Total_Price_LKR'].sum().sort_values(ascending=False).reset_index()
product_revenue['Total_Price_LKR'] = product_revenue['Total_Price_LKR'] / 1000000
top_products_by_revenue_md = product_revenue.head(15).to_markdown(index=False)
bottom_products_by_revenue_md = product_revenue.tail(10).sort_values('Total_Price_LKR').to_markdown(index=False)

product_quantity = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).reset_index()
top_products_by_quantity_md = product_quantity.head(15).to_markdown(index=False)

# --- NEW: Day-of-Week Revenue Trend (in Millions LKR) ---
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekly_sales = df.groupby('Day')['Total_Price_LKR'].sum().reset_index()
weekly_sales['Total_Price_LKR'] = weekly_sales['Total_Price_LKR'] / 1000000
weekly_sales['Day'] = pd.Categorical(weekly_sales['Day'], categories=day_order, ordered=True)
weekly_sales = weekly_sales.sort_values('Day')
weekly_sales_md = weekly_sales.to_markdown(index=False)

# --- NEW: Hourly Revenue Trend (in Millions LKR) ---
hourly_sales = df.groupby('Hour')['Total_Price_LKR'].sum().reset_index()
hourly_sales['Total_Price_LKR'] = hourly_sales['Total_Price_LKR'] / 1000000
hourly_sales_md = hourly_sales.to_markdown(index=False)

# --- Customer Segmentation (RFM + K-Means) ---
customers, cluster_counts, segment_summary_md = get_segment_summary(df)
total_customers = customers['CustomerID'].nunique()

# --- NEW: Annual Sales Forecast (shared with the Forecast tab on Sales Performance) ---
history_recent, forecast_dataset, forecast_combined, forecast_summary_md, forecast_peak_period, forecast_model = \
    get_sales_forecast(df, is_uploaded)

avg_recent_actual = history_recent['Sales'].mean()
avg_forecast = forecast_dataset['Sales'].mean()
forecast_trend = "upward" if avg_forecast > avg_recent_actual else "downward"
forecast_trend_pct = abs((avg_forecast - avg_recent_actual) / avg_recent_actual) * 100 if avg_recent_actual else 0
forecast_prev_year_label = history_recent['Year_Label'].iloc[0]
forecast_year_label = forecast_dataset['Year_Label'].iloc[0]

# --- STREAMLIT CHAT UI ---
if "model" not in st.session_state:
    st.session_state['model'] = 'llama3-70b-8192'

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response ONLY when a new prompt is submitted
    with st.chat_message("assistant"):

        # --- STRUCTURING THE SYSTEM CONTEXT ---
        system_prompt = f"""You are 'Insight.AI', the specialized chatbot for 'Retail Radar' analytical platform.
        Your job is to deliver concise data insights based on the matrices provided below.
        All revenue metrics are customized for Sri Lankan Rupees (LKR).

        [DESCRIPTIVE STATISTICS]:
        {describe}

        [CORRELATION MATRIX]:
        {correlation}

        [YEARLY REVENUE (In Millions LKR)]:
        {year_data_md}

        [MONTHLY REVENUE BREAKDOWN (In Millions LKR)]:
        {monthly_revenue_md}

        [DISTRICT-WISE REVENUE PERFORMANCE (In Lakhs/100k LKR)]:
        {districtwise_data_md}

        [TOP 15 PRODUCTS BY REVENUE (In Millions LKR)]:
        {top_products_by_revenue_md}

        [TOP 15 PRODUCTS BY SOLD QUANTITY (Units)]:
        {top_products_by_quantity_md}

        [BOTTOM 10 PRODUCTS BY REVENUE (In Millions LKR)]:
        {bottom_products_by_revenue_md}

        [DAY-OF-WEEK REVENUE TREND (In Millions LKR)]:
        {weekly_sales_md}

        [HOURLY REVENUE TREND (In Millions LKR)]:
        {hourly_sales_md}

        [CUSTOMER SEGMENTATION OVERVIEW]:
        Total unique customers: {total_customers}
        Customers are grouped via RFM (Recency, Frequency, Monetary) analysis and K-Means clustering
        into behavioral segments. Segment name, customer count, and average spend per customer
        (in thousand LKR) are shown below:
        {segment_summary_md}

        [SALES FORECAST — NEXT YEAR, MONTHLY (In Millions LKR)]:
        A RandomForestRegressor trained on monthly revenue projects a {forecast_trend} trend for the
        next year ({forecast_year_label}) versus the previous year ({forecast_prev_year_label}) of
        actual revenue (recent actual average: {avg_recent_actual:.2f}M LKR/month vs. forecast
        average: {avg_forecast:.2f}M LKR/month, a {forecast_trend_pct:.1f}% difference). Projected
        peak month: {forecast_peak_period['Date'].strftime('%B %Y')} ({forecast_peak_period['Quarter_Label']}) at
        {forecast_peak_period['Sales']:.2f}M LKR. This forecast covers only the 12 months (1 year)
        immediately following the dataset's last recorded month — it does not extend further into the
        future. Monthly forecast values:
        {forecast_summary_md}

        Rules: Keep answers business-oriented, direct, and factual. Always clarify whether monetary
        values are displayed in Millions, Lakhs, or Thousands based on the data keys above. When asked
        about customers, loyalty, churn risk, or segments, use the CUSTOMER SEGMENTATION OVERVIEW table
        rather than guessing — if a segment isn't in the table, say so instead of inventing one. When
        asked about timing, footfall, staffing, or "best time to shop/promote", use the DAY-OF-WEEK and
        HOURLY REVENUE TREND tables rather than guessing. When asked about products, bestsellers, top
        sellers, or worst/weakest performers, use the TOP/BOTTOM PRODUCTS BY REVENUE and TOP PRODUCTS BY
        SOLD QUANTITY tables rather than guessing — if a product isn't in these tables, say you only
        have visibility into the top and bottom performers, not the full catalog. When asked about future
        sales, forecasts, projections, expected performance, or a specific upcoming quarter, use the
        SALES FORECAST table rather than guessing — if asked about a month or quarter beyond the 1-year
        forecast horizon, say the forecast doesn't extend that far rather than inventing a number.

        Answer format: Before answering a "best/worst/highest/lowest/top" question, scan the full
        relevant table yourself and identify the single row with the correct max or min value — do
        this silently, do not narrate the scanning process. State ONLY that final answer as your
        opening sentence, with its exact figure (e.g. "The best performing hour is 18:00, with 22.0
        million LKR in revenue."). Never present one answer and then correct yourself to a different
        one in the same response — if you catch a discrepancy, resolve it before writing, not after.
        Do not list runner-up or nearby values unless the user explicitly asks for a ranking or
        comparison. Keep answers to 1-3 sentences unless the user asks for more detail or a breakdown."""

        api_messages = [{"role": "system", "content": system_prompt}]
        
        # Safely append the conversation history
        api_messages.extend([
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ])

        # Pass the clean list to the API
        stream = client.chat.completions.create(
            model=st.session_state['model'],
            messages=api_messages,
            stream=True,
        )
        
        # Parse text chunks out of the Groq stream objects for st.write_stream
        def text_generator():
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        response = st.write_stream(text_generator())
        
    # Append to history AFTER streaming finishes
    st.session_state.messages.append({"role": "assistant", "content": response})