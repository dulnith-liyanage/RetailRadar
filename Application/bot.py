import streamlit as st
from groq import Groq
from utils import get_raw_data, clean_data
import pandas as pd

# Initialize Groq Client
client = Groq(api_key=st.secrets['API_KEY'])

@st.cache_data
def load_data():  # add load data function
    df = pd.read_csv("../data/output/srilanka_retail_2020_2026_small.csv")
    return df.head(100).to_string() 

dataset_string = load_data()

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

# --- STREAMLIT CHAT UI ---
if "model" not in st.session_state:
    st.session_state["model"] = "llama-3.3-70b-versatile"

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
    # 1. Create the base array with your system rules
        api_messages = [
            {   "role": "system", 
                "content": f"Your name is 'Insight.AI'. You are a chatbot of 'Retail Radar', a service used to analyze retail data. Use this dataset to answer questions:\n\n{dataset_string}"
               # changed this 
            }
        ]
        
        # --- 2. STRUCTURING THE SYSTEM CONTEXT ---
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
        
        Rules: Keep answers business-oriented, direct, and factual. Always clarify whether monetary values are displayed in Millions or Lakhs based on the data keys above."""

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
