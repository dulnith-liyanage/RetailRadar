import folium
import streamlit as st
import folium
from streamlit_folium import st_folium
from calculator_api import Calculator

cal = Calculator()
district = cal.dis()

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
    legend_name='Total Price in LKR'
).add_to(sri_lanka_map)
###

# call to render Folium map in Streamlit
st_data = st_folium(sri_lanka_map, width=700, height=500)