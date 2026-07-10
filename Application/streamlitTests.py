import pandas as pd

df = pd.read_csv("../data/output/srilanka_retail_2020_2026.csv")

year_data = df.groupby('InvoiceDate')['Total_Price_LKR'].sum().reset_index()
year_data['InvoiceDate'] =  year_data['InvoiceDate'][0][:4]

year_data = year_data.rename(columns={'InvoiceDate': 'Year'})
x = year_data.loc[year_data['Year'] > 2020]
print(x)