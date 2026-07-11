import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pylab as plt
import streamlit as st

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

# Drop the first row of the district GeoDataFrame
district = district.iloc[1:]

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# --- NEW: Change Axis and Numbers Color ---
# 1. Change the color of the surrounding boundary box lines (Spines)
for spine in ax.spines.values():
    spine.set_color('white')  # Can use 'white', 'grey', or hex '#000000'

# 2. Change the color of the axis numbers and tick marks
ax.tick_params(axis='both', colors='white', labelsize=10)


# 3. Generate the map plot
district.plot(column='Total_Price_LKR', cmap='Blues', legend=True, ax=ax)

# 4. Render safely
st.pyplot(fig, transparent=True)
