import streamlit as st

welcome_page = st.Page("welcome.py", title="Welcome")
sales_performance_page = st.Page("sales_performance.py", title="Sales Performance", icon="📈")
rfm_page = st.Page("rfm.py", title="Customer Segments", icon="👥")
chatbot_page = st.Page("bot.py", title = "Insight.AI", icon="🤖")
pg = st.navigation([welcome_page, sales_performance_page, rfm_page, chatbot_page])
pg.run()