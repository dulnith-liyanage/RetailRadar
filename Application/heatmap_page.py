import folium
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pylab as plt

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

geo_data = gpd.read_file("../data/geodata/District_geo.json")
geo_data = geo_data[['ADM2_EN', 'geometry']].rename(columns={'ADM2_EN': 'District'})

dis_df = df.groupby('District')['Total_Price_LKR'].sum().sort_values(ascending=False).reset_index()
district = geo_data.merge(dis_df, how='left', left_on='District', right_on='District')

st.markdown("### Districtwise Distribution of the Total Price")
st.sidebar.markdown("*This heat map represents the districtwise distribution of the Total Price*")

district = district.iloc[1:]
fig, ax = plt.subplots(figsize=(10, 8))
district["Total_Price_LKR"] = district["Total_Price_LKR"]/1000000  # Convert to millions

# for spine in ax.spines.values():
#     spine.set_color('white') 
# ax.tick_params(axis='both', colors='white', labelsize=10)
ax.axis('off')

district = district.sort_values(by='Total_Price_LKR', ascending=True)
district.plot(column='Total_Price_LKR', cmap='Purples', legend=True, ax=ax, color='white')

st.pyplot(fig, clear_figure=True, transparent=True)

district_data = df.groupby('District')['Total_Price_LKR'].sum().reset_index()
district_data['Total_Price_LKR'] = district_data['Total_Price_LKR'] / 1000000

my_chart = st.bar_chart(district_data, x='District', y='Total_Price_LKR', x_label='District', y_label='Total Price in Million LKR', color="#C57AF4")