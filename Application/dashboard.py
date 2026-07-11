import streamlit as st

welcome_page = st.Page("welcome.py", title="Welcome")
plots_page = st.Page("chart_page.py", title="Sales Performance", icon="📈")
heatmap_page = st.Page("heatmap_page.py", title="Districtwise Distribution", icon="📌")

pg = st.navigation([welcome_page, plots_page, heatmap_page])
pg.run()