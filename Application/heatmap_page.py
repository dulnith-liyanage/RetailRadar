import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pylab as plt

st.sidebar.markdown("*This heat map represents the districtwise distribution of the Total Price*")

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
district = district.iloc[1:]

district["Total_Price_LKR"] = district["Total_Price_LKR"]/1000000  # Convert to millions

district = district[district['Total_Price_LKR'] > 0] # Remove rows with zero Total_Price_LKR values

st.markdown("## Districtwise Distribution of the Total Price")
st.write("")
st.markdown("#### Bar Chart Representation")
district_data = df.groupby('District')['Total_Price_LKR'].sum().reset_index()
district_data['Total_Price_LKR'] = district_data['Total_Price_LKR'] / 1000000

# Create a bar chart
st.bar_chart(district_data, x='District', y='Total_Price_LKR',
              x_label='District'
             , y_label='Total Price in Million LKR', color="#8aadf4")

st.markdown("#### Heatmap Representation")
# Create a choropleth map
fig, ax = plt.subplots(figsize=(10, 8))

ax.axis('off')

district = district.sort_values(by='Total_Price_LKR', ascending=True)
district.plot(column='Total_Price_LKR', cmap="Blues", legend=True, ax=ax, color='white')

st.pyplot(fig, clear_figure=True, transparent=True)
