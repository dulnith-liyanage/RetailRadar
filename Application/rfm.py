from utils import get_raw_data, clean_data
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

raw_df, is_uploaded = get_raw_data()
st.sidebar.markdown(
    "*Currently using uploaded file.*" if is_uploaded
    else "*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*"
)

st.markdown("# Customer Segmentation")

df = clean_data(raw_df)

snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Quantity", "sum")
).reset_index()

rfm["R-Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["F-Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["M-Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

# --- KMeans Clustering ---

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm[["Recency", "Frequency", "Monetary"]])

kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
rfm["Cluster"] = kmeans.fit_predict(rfm_scaled)

profile = rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean().reset_index()

# Define bins and labels for R, F, M tiers
r_bins = rfm['Recency'].quantile([0.2, 0.4, 0.6, 0.8]).values
f_bins = rfm['Frequency'].quantile([0.2, 0.4, 0.6, 0.8]).values
m_bins = rfm['Monetary'].quantile([0.2, 0.4, 0.6, 0.8]).values

# Function to assign tiers based on bins
def tier(value, bins, labels):
    for i, b in enumerate(bins):
        if value <= b:
            return labels[i]
    return labels[-1]

recency_labels = ['Very Recent', 'Recent', 'Moderate', 'Lapsing', 'Lapsed']
frequency_labels = ['Rare', 'Infrequent', 'Occasional', 'Frequent', 'Very Frequent']
monetary_labels = ['Very Low Value', 'Low Value', 'Medium Value', 'High Value', 'Very High Value']

profile['R_Tier'] = profile['Recency'].apply(lambda v: tier(v, r_bins, recency_labels))
profile['F_Tier'] = profile['Frequency'].apply(lambda v: tier(v, f_bins, frequency_labels))
profile['M_Tier'] = profile['Monetary'].apply(lambda v: tier(v, m_bins, monetary_labels))

profile['Label'] = profile['R_Tier'] + ", " + profile['F_Tier'] + ", " + profile['M_Tier']

customers = profile.merge(rfm[['Cluster', 'CustomerID']], on='Cluster', how='left')
customers = customers[["CustomerID", "Cluster", "Label"]]

customer_total_spent = df.groupby("CustomerID")["Total_Price_LKR"].sum().reset_index()
customers = customers.merge(customer_total_spent, on='CustomerID', how='left')

## --- K Means Clustering Visualization ---

# Create a mapping from Cluster to Label for use in the pie chart
label_lookup = dict(zip(profile['Cluster'].astype(str), profile['Label']))
label_expr = " : ".join(f"datum.value == '{k}' ? '{v}'" for k, v in label_lookup.items()) + " : ''"

# Prepare data for pie chart
cluster_counts = rfm['Cluster'].value_counts().reset_index()
cluster_counts.columns = ['Cluster', 'Count']
cluster_counts = cluster_counts.merge(
    profile[['Cluster', 'Label']],
    on='Cluster',
    how='left'
)

pfig = px.pie(
        cluster_counts, 
        names='Label', 
        values='Count', 
        hole=0.7,  # Turns the pie chart into a donut
        # Matching the color palette sequence roughly to your current pastel colors:
        color_discrete_sequence=['#f3ded7', '#c29df1', '#ec8792', '#eed1a2', '#a2db9a', '#92d6e3', '#8db2f3'] 
    )

# Style the central hole text, gaps between slices, and the horizontal legend
unique_customer_count = rfm['CustomerID'].nunique()
pfig.update_layout(
    annotations=[
        # Top line text inside hole
            dict(text='TOTAL UNIQUE CUSTOMERS', x=0.5, y=0.54, font_size=13, showarrow=False, font_color="#a0aab8",),
        # Bottom main calculation text inside hole
            dict(text=unique_customer_count, x=0.5, y=0.47, font_size=20, showarrow=False, font_color="white")
    ],
    legend=dict(
        orientation="h",       # Makes the legend horizontal instead of vertical
        yanchor="bottom",
        y=-0.35,               # Positions legend neatly beneath the chart
        xanchor="center",
        x=0.5,
        title=None,
    ),
    showlegend=True,
    margin=dict(t=20, b=20, l=20, r=20)  # Adjust margins to reduce whitespace
)

# Hide the text percentages on the chart slices and add the clean white borders
pfig.update_traces(
    textinfo='none', 
    marker=dict(line=dict(color='#0e1117', width=4)) # Match this hex color to your dashboard background
)

st.plotly_chart(pfig, use_container_width=True)

# Top Customers
top_customers = customers.sort_values(by="Total_Price_LKR", ascending=False).head(10)
st.write("### Top 10 Customers by Total Amount Spent")
st.dataframe(top_customers[["CustomerID", "Total_Price_LKR", "Label"]].reset_index(drop=True))