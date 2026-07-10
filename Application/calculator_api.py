import pandas as pd
import geopandas as gpd

class Calculator:
    def __init__(self):
        df = pd.read_csv("../data/output/srilanka_retail_2020_2026.csv")
        geo_data = gpd.read_file("../data/geodata/District_geo.json")
        geo_data = geo_data[['ADM2_EN', 'geometry']].rename(columns={'ADM2_EN': 'District'})
        dis_df = df.groupby('District')['Total_Price_LKR'].sum().sort_values(ascending=False).reset_index()
        dis = geo_data.merge(dis_df, how='left', left_on='District', right_on='District')
        self.district = dis
        self.df = df
        
    def dis(self):
        return self.district
    
    def dataframe(self):
        return self.df