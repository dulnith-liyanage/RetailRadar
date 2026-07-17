import streamlit as st
from groq import Groq
import pandas as pd

client = Groq(api_key=st.secrets['API_KEY'])

@st.cache_data
def load_data():  # add load data function
    df = pd.read_csv("../data/output/srilanka_retail_2020_2026_small.csv")
    return df.head(100).to_string() 

dataset_string = load_data()

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
        
        # 2. Safely append the conversation history
        api_messages.extend([
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ])

        # 3. Pass the clean list to the API
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
