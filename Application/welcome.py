import streamlit as st
import pandas as pd
from utils import get_raw_data, clean_data

st.set_page_config(page_title="Welcome")

NORD_BG = "#2E3440"          
NORD_CARD_BG = "#3B4252"     
NORD_TEXT_MUTED = "#A9B4C4"  
NORD_FROST = "#88C0D0"
NORD_FROST_DEEP = "#5E81AC"
NORD_ORANGE = "#D08770"
NORD_PURPLE = "#B48EAD"
NORD_GREEN = "#A3BE8C"

# BRANDING
st.markdown(
    f"<p style='color:{NORD_TEXT_MUTED}; font-size:0.85rem; margin-bottom:0;'>"
    "DATA ODYSSEY 2026 &nbsp;·&nbsp; AI AND DATA SCIENCE CLUB &nbsp;·&nbsp; "
    "GENERAL SIR JOHN KOTELAWALA DEFENCE UNIVERSITY</p>",
    unsafe_allow_html=True
)

st.write("# Welcome to Retail Radar")
st.caption(
    "AI-powered retail analytics for the Sri Lankan market — revenue trends, future predictions "
    "regional performance, customer segmentation, and an in-app AI analyst, all in one dashboard."
)

# st.sidebar.success("*Select a module to begin.*")
# DATA SOURCE
st.markdown("### Get Started")
st.markdown(
    "Upload your own retail CSV below, or skip straight to the dashboard — "
    "it's already running on our built-in demo dataset covering Sri Lankan retail "
    "transactions from 2020 to 2026."
)

uploaded_file = st.file_uploader("Choose a file (.csv)", accept_multiple_files=False, type=".csv")

if uploaded_file:
    dataframe = pd.read_csv(uploaded_file)
    st.session_state["dataset"] = dataframe

    st.success("Dataset successfully uploaded and saved to memory!")

# Data Preview & Overview
raw_df, is_uploaded = get_raw_data()
df = clean_data(raw_df)

st.markdown("### Data Overview")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown(f"<span style='color:{NORD_FROST};'>📦</span> Total Transactions", unsafe_allow_html=True)
        st.markdown(f"## {df['InvoiceNo'].nunique():,}")

with col2:
    with st.container(border=True):
        st.markdown(f"<span style='color:{NORD_PURPLE};'>👥</span> Total Customers", unsafe_allow_html=True)
        st.markdown(f"## {df['CustomerID'].nunique():,}")

with col3:
    with st.container(border=True):
        st.markdown(f"<span style='color:{NORD_GREEN};'>💰</span> Total Revenue (M LKR)", unsafe_allow_html=True)
        st.markdown(f"## {df['Total_Price_LKR'].sum() / 1_000_000:,.1f}")

st.divider()

# EXPLORE THE DASHBOARD — clickable feature previews
st.markdown("### Explore the Dashboard")

fcol1, fcol2, fcol3 = st.columns(3)

with fcol1:
    with st.container(border=True):
        st.markdown(f"<span style='color:{NORD_FROST_DEEP}; font-size:1.4rem;'>📈</span>", unsafe_allow_html=True)
        st.markdown("**Sales Performance**")
        st.markdown(
            f"<span style='color:{NORD_TEXT_MUTED};'>Revenue trends by year, month, weekday and "
            "hour, revenue heatmap, top products, and districtwise distribution.</span>",
            unsafe_allow_html=True
        )
        st.page_link("sales_performance.py", label="Open Sales Performance", icon="📈")

with fcol2:
    with st.container(border=True):
        st.markdown(f"<span style='color:{NORD_PURPLE}; font-size:1.4rem;'>👥</span>", unsafe_allow_html=True)
        st.markdown("**Customer Segments**")
        st.markdown(
            f"<span style='color:{NORD_TEXT_MUTED};'>RFM analysis and K-Means clustering group "
            "customers into behavioral segments like Champions and At-Risk VIPs.</span>",
            unsafe_allow_html=True
        )
        st.page_link("rfm.py", label="Open Customer Segments", icon="👥")

with fcol3:
    with st.container(border=True):
        st.markdown(f"<span style='color:{NORD_ORANGE}; font-size:1.4rem;'>💡</span>", unsafe_allow_html=True)
        st.markdown("**Insight.AI**")
        st.markdown(
            f"<span style='color:{NORD_TEXT_MUTED};'>Ask questions in plain language and get answers "
            "grounded in the same data shown across the dashboard.</span>",
            unsafe_allow_html=True
        )
        st.page_link("bot.py", label="Open Insight.AI", icon="💡")

#Who are we...?

st.divider()
with st.container(border=True):
    st.markdown("### Who are Meridian?")
    st.markdown("""We are a group of passionate data science 
    enthusiasts from the University of Moratuwa, Batch 25, 
    who came together to tackle this competition with a shared vision: 
    applying analytical thinking to real-world problems. 
    Through this project, we combined our diverse expertise to design, implement, 
    and refine solutions that reflect our commitment to 
    innovation, teamwork, and practical impact.""")
    contributors = [
    {
        "name": "Dulnith Liyanage",
        "role": "Coordinator / EDA / Segmentations and visualizations",
        "img": "https://media.licdn.com/dms/image/v2/D5603AQFWoeb_1wnusw/profile-displayphoto-crop_800_800/B56Z.nSKIoIoAI-/0/1785217983932?e=1787788800&v=beta&t=fsSpiCXTXxh-j-7wtKiG2GH9LQPC2IGS7MC6d9ftvnM",  # LinkedIn image URL
        "lin": "https://www.linkedin.com/in/dulnithliyanage/"
    },
    {
        "name": "Thenul Sahansa",
        "role": "Dashboard / Prediction algorithms",
        "img": "https://media.licdn.com/dms/image/v2/D4E03AQGg0Q8Rl9cutQ/profile-displayphoto-crop_800_800/B4EZozIW9TIQAI-/0/1761794423516?e=1787788800&v=beta&t=ZuRnq3QtE80gwz-zvxF2pR4ibJPE-Dt6-1qfwdADNn4",
        "lin": "https://www.linkedin.com/in/thenulsahansa/"
    },
    {
        "name": "Dimuth Wickramasinghe",
        "role": "Chatbot / Telebot",
        "img": "https://media.licdn.com/dms/image/v2/D4E03AQHqvqX185w7Sw/profile-displayphoto-crop_800_800/B4EZpEpOEQIUAI-/0/1762088262027?e=1787788800&v=beta&t=ltMB1kaKaeau-85bDzIxtZE3cfOi8bsyuuHCjRBSHhw",
        "lin": "https://www.linkedin.com/in/dimuth-wickramasinghe-1a5765380/"
    },
    {
        "name": "Bihandu Liyanage",
        "role": "Data collection / Feature engineering",
        "img": "https://tse3.mm.bing.net/th/id/OIP.IuRnbsXuvqX9BDNNGK1-IQHaHG?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
        "lin": "https://www.linkedin.com/in/bihandu-liyanage-775b24376/"
    },
]
    for contributor in contributors:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(contributor["img"], width=60)
        with col2:
            st.markdown(f"**[{contributor['name']}]({contributor["lin"]})**  \n*{contributor['role']}*")