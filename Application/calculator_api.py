import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

class Calculator:
    def __init__(self):
        df = pd.read_csv("D:\IBM-Datascientist\Python\RetailRadar\data\output\srilanka_retail_2020_2026_small.csv")
        geo_data = gpd.read_file("D:\IBM-Datascientist\Python\RetailRadar\data\geodata\District_geo.json")
        geo_data = geo_data[['ADM2_EN', 'geometry']].rename(columns={'ADM2_EN': 'District'})
        dis_df = df.groupby('District')['Total_Price_LKR'].sum().sort_values(ascending=False).reset_index()
        dis = geo_data.merge(dis_df, how='left', left_on='District', right_on='District')
        self.district = dis
        self.df = df
        
    def dis(self):
        return self.district
    def chart(self):
        year_data = self.df.groupby('Year')['Total_Price_LKR'].sum().reset_index()
        year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000
        year_data.plot(x='Year', y='Total_Price_LKR', kind='bar', title='Earnings in Million LKR by Year', xlabel='Year', ylabel='Total Price in Million LKR', legend=None, color='green', figsize=(8, 6))

    def dataframe(self):
        return self.df