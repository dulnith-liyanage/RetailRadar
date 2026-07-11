import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pylab as plt
import matplotlib.colors as mcolors
import altair as alt

st.sidebar.markdown("*This heat map and bar chart represents the districtwise distribution of the Total Price*")

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

# Theme for heatmap and bar chart
catppuccin_red_shades = [
    "#fde8ee",
    "#f6c0cf",
    "#ec9bb2",
    "#df7a96",
    "#cf5b7c",
    "#bb4163",
    "#913c54",
    "#6b3443",
    "#482831",
]

catppuccin_red_cmap = mcolors.LinearSegmentedColormap.from_list(
    "catppuccin_red", catppuccin_red_shades
)

geo_data = gpd.read_file("../data/geodata/District_geo.json")
geo_data = geo_data[['ADM2_EN', 'geometry']].rename(columns={'ADM2_EN': 'District'})

dis_df = df.groupby('District')['Total_Price_LKR'].sum().sort_values(ascending=False).reset_index()
district = geo_data.merge(dis_df, how='left', left_on='District', right_on='District')
district = district.iloc[1:]

district["Total_Price_LKR"] = district["Total_Price_LKR"]/1000000  # Convert to millions

st.markdown("# Districtwise Distribution")

col1, col2 = st.columns(2, gap='large')

with col1:
    # Create a choropleth map using Matplotlib
    fig, ax = plt.subplots(figsize=(5, 5))
    district.plot(column='Total_Price_LKR', cmap=catppuccin_red_cmap, ax=ax, legend=False,
                   missing_kwds={"color": "white", "label": "No data"})
    ax.axis('off')
    st.pyplot(fig, use_container_width=False, transparent=True)

with col2:
    # Create a bar chart
    st.write("")
    st.write("")
    chart = (
        alt.Chart(district)
        .mark_bar()
        .encode(
            y=alt.Y('District', sort='-x'),
            x=alt.X('Total_Price_LKR', title='Total Revenue in Million LKR'),
            color=alt.Color('Total_Price_LKR', scale=alt.Scale(range=catppuccin_red_shades), legend=None),
        )
    )

    st.altair_chart(chart, use_container_width=False)

