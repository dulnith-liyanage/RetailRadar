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
customers, cluster_counts, segment_summary_md, _ = get_segment_summary(df)
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
    st.session_state['model'] = 'openai/gpt-oss-20b'

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

        def get_revenue_data():
            return f"[YEARLY REVENUE]\n{year_data_md}\n[MONTHLY REVENUE]\n{monthly_revenue_md}\n[DISTRICT REVENUE]\n{districtwise_data_md}"

        def get_product_data():
            return f"[TOP PRODUCTS BY REVENUE]\n{top_products_by_revenue_md}\n[TOP PRODUCTS BY QUANTITY]\n{top_products_by_quantity_md}\n[BOTTOM PRODUCTS]\n{bottom_products_by_revenue_md}"

        def get_segment_data():
            return f"[CUSTOMER SEGMENTS]\n{segment_summary_md}"

        def get_forecast_data():
            return f"[SALES FORECAST]\n{forecast_summary_md}"

        def get_timing_data():
            return f"[WEEKLY SALES]\n{weekly_sales_md}\n[HOURLY SALES]\n{hourly_sales_md}"

        available_tools = {
            "get_revenue_data": get_revenue_data,
            "get_product_data": get_product_data,
            "get_segment_data": get_segment_data,
            "get_forecast_data": get_forecast_data,
            "get_timing_data": get_timing_data,
        }

        tools = [
            {"type": "function", "function": {"name": "get_revenue_data", "description": "Get yearly, monthly, and district revenue."}},
            {"type": "function", "function": {"name": "get_product_data", "description": "Get top and bottom performing products."}},
            {"type": "function", "function": {"name": "get_segment_data", "description": "Get customer segments, RFM, and K-Means data."}},
            {"type": "function", "function": {"name": "get_forecast_data", "description": "Get the next 12 months sales forecast."}},
            {"type": "function", "function": {"name": "get_timing_data", "description": "Get revenue trends by day of week and hour of day."}}
        ]

        # --- STRUCTURING THE SYSTEM CONTEXT ---
        system_prompt = f"""You are 'Insight.AI', the specialized chatbot for 'Retail Radar'.
You have tools to fetch specific data matrices. Always call the appropriate tool when a user asks for data you don't have in context.
Keep answers concise, direct, and factual.
[DESCRIPTIVE STATISTICS]:\n{describe}\n[CORRELATION MATRIX]:\n{correlation}"""

        api_messages = [{"role": "system", "content": system_prompt}]
        
        # Safely append the conversation history
        api_messages.extend([
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ])

        # Pass the clean list to the API (non-streaming to check tools)
        response_msg = client.chat.completions.create(
            model=st.session_state['model'],
            messages=api_messages,
            tools=tools,
            tool_choice="auto"
        ).choices[0].message
        
        if response_msg.tool_calls:
            api_messages.append(response_msg)
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                if func_name in available_tools:
                    func_response = available_tools[func_name]()
                    api_messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_response,
                    })
            
            # Second call (streaming)
            stream = client.chat.completions.create(
                model=st.session_state['model'],
                messages=api_messages,
                stream=True,
                tools=tools,
            )
            def text_generator():
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            response = st.write_stream(text_generator())
        else:
            response = response_msg.content or ""
            st.write(response)
        
    # Append to history AFTER streaming finishes
    st.session_state.messages.append({"role": "assistant", "content": response})