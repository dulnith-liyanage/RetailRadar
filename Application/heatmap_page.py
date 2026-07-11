import folium
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd

df = pd.read_csv("../data/output/srilanka_retail_2020_2026.csv")
geo_data = gpd.read_file("../data/geodata/District_geo.json")
geo_data = geo_data[['ADM2_EN', 'geometry']].rename(columns={'ADM2_EN': 'District'})
dis_df = df.groupby('District')['Total_Price_LKR'].sum().sort_values(ascending=False).reset_index()
dis_df['Total_Price_LKR'] = dis_df['Total_Price_LKR'] / 10000000
district = geo_data.merge(dis_df, how='left', left_on='District', right_on='District')

st.markdown("### Districtwise Distribution of the Total Price")
st.sidebar.markdown("*This heat map represents the districtwise distribution of the Total Price*")

sri_lanka_map = folium.Map(location=[7.8731, 80.7718], zoom_start=7)

folium.Choropleth(
    geo_data=district,
    name='choropleth',
    data=district,
    columns=['District', 'Total_Price_LKR'],
    key_on='feature.properties.District',
    fill_color='Blues',
    fill_opacity=0.8,
    line_opacity=0.2,
    legend_name='Total Price in Millions (LKR)'
).add_to(sri_lanka_map)

st_data = st_folium(sri_lanka_map, width=700, height=500)