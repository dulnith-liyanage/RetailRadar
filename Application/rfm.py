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


#Customer segments
customer_segments = {
    # --- VERY RECENT ---
    "Very Recent, Very Frequent, Very High Value": {"name": "Champions"},
    "Very Recent, Very Frequent, High Value": {"name": "Top Tier Advocates"},
    "Very Recent, Very Frequent, Medium Value": {"name": "High-Volume Buyers"},
    "Very Recent, Very Frequent, Low Value": {"name": "Promotional Power Users"},
    "Very Recent, Very Frequent, Very Low Value": {"name": "Active Trialists"},
    
    "Very Recent, Frequent, Very High Value": {"name": "High-Value Movers"},
    "Very Recent, Frequent, High Value": {"name": "Core Loyals"},
    "Very Recent, Frequent, Medium Value": {"name": "Steady Streamers"},
    "Very Recent, Frequent, Low Value": {"name": "Frequent Bargain Hunters"},
    "Very Recent, Frequent, Very Low Value": {"name": "Highly Engaged Starters"},
    
    "Very Recent, Occasional, Very High Value": {"name": "Big Ticket Whales"},
    "Very Recent, Occasional, High Value": {"name": "Premium Onboarders"},
    "Very Recent, Occasional, Medium Value": {"name": "Growing Potentials"},
    "Very Recent, Occasional, Low Value": {"name": "New Starters"},
    "Very Recent, Occasional, Very Low Value": {"name": "Casual Trials"},
    
    "Very Recent, Infrequent, Very High Value": {"name": "High-Value Explorers"},
    "Very Recent, Infrequent, High Value": {"name": "Affluent Prospects"},
    "Very Recent, Infrequent, Medium Value": {"name": "Mid-Tier Prospects"},
    "Very Recent, Infrequent, Low Value": {"name": "New Prospects"},
    "Very Recent, Infrequent, Very Low Value": {"name": "Minimal Prospects"},
    
    "Very Recent, Rare, Very High Value": {"name": "Instant Luxury Buyers"},
    "Very Recent, Rare, High Value": {"name": "Premium First-Timers"},
    "Very Recent, Rare, Medium Value": {"name": "Curious Newcomers"},
    "Very Recent, Rare, Low Value": {"name": "One-Time Experimenters"},
    "Very Recent, Rare, Very Low Value": {"name": "Entry-Level Registrations"},

    # --- RECENT ---
    "Recent, Very Frequent, Very High Value": {"name": "Consistent Champions"},
    "Recent, Very Frequent, High Value": {"name": "Reliable Enthusiasts"},
    "Recent, Very Frequent, Medium Value": {"name": "Active Volume Buyers"},
    "Recent, Very Frequent, Low Value": {"name": "Systematic Bargainers"},
    "Recent, Very Frequent, Very Low Value": {"name": "Active Minimalists"},
    
    "Recent, Frequent, Very High Value": {"name": "High-Value Core"},
    "Recent, Frequent, High Value": {"name": "Standard Core Loyals"},
    "Recent, Frequent, Medium Value": {"name": "Mid-Market Regulars"},
    "Recent, Frequent, Low Value": {"name": "Regular Discount Seekers"},
    "Recent, Frequent, Very Low Value": {"name": "Low-Value Regulars"},
    
    "Recent, Occasional, Very High Value": {"name": "Spur-of-the-Moment Whales"},
    "Recent, Occasional, High Value": {"name": "Nurture Candidates"},
    "Recent, Occasional, Medium Value": {"name": "Satisfied Neutrals"},
    "Recent, Occasional, Low Value": {"name": "Shallow Buyers"},
    "Recent, Occasional, Very Low Value": {"name": "Low-Priority Neutrals"},
    
    "Recent, Infrequent, Very High Value": {"name": "Selective Premium Spenders"},
    "Recent, Infrequent, High Value": {"name": "Warm Prospects"},
    "Recent, Infrequent, Medium Value": {"name": "Standard Prospects"},
    "Recent, Infrequent, Low Value": {"name": "Developing Shoppers"},
    "Recent, Infrequent, Very Low Value": {"name": "Low-Margin Contacts"},
    
    "Recent, Rare, Very High Value": {"name": "Spontaneous Premium Spenders"},
    "Recent, Rare, High Value": {"name": "Casual Premium Buyers"},
    "Recent, Rare, Medium Value": {"name": "Standard Visitors"},
    "Recent, Rare, Low Value": {"name": "Passing Trade"},
    "Recent, Rare, Very Low Value": {"name": "Inactive New Leads"},

    # --- MODERATE ---
    "Moderate, Very Frequent, Very High Value": {"name": "Slowing VIPs"},
    "Moderate, Very Frequent, High Value": {"name": "Steady Volume Customers"},
    "Moderate, Very Frequent, Medium Value": {"name": "Stable Bulk Purchasers"},
    "Moderate, Very Frequent, Low Value": {"name": "Habitual Coupon Shoppers"},
    "Moderate, Very Frequent, Very Low Value": {"name": "Low-Yield Regulars"},
    
    "Moderate, Frequent, Very High Value": {"name": "High-Value Mainstays"},
    "Moderate, Frequent, High Value": {"name": "Standard Mainstays"},
    "Moderate, Frequent, Medium Value": {"name": "Middle-Tier Core"},
    "Moderate, Frequent, Low Value": {"name": "Value-Conscious Regulars"},
    "Moderate, Frequent, Very Low Value": {"name": "Marginal Regulars"},
    
    "Moderate, Occasional, Very High Value": {"name": "Intermittent Spenders"},
    "Moderate, Occasional, High Value": {"name": "Periodic Premium Shoppers"},
    "Moderate, Occasional, Medium Value": {"name": "Average Consumers"},
    "Moderate, Occasional, Low Value": {"name": "Casual Occasionals"},
    "Moderate, Occasional, Very Low Value": {"name": "Unprofitable Occasionals"},
    
    "Moderate, Infrequent, Very High Value": {"name": "Infrequent Luxury Accounts"},
    "Moderate, Infrequent, High Value": {"name": "Unrealized Value Accounts"},
    "Moderate, Infrequent, Medium Value": {"name": "Quiet Neutrals"},
    "Moderate, Infrequent, Low Value": {"name": "Fading Accounts"},
    "Moderate, Infrequent, Very Low Value": {"name": "Stagnant Leads"},
    
    "Moderate, Rare, Very High Value": {"name": "Isolated Event Buyers"},
    "Moderate, Rare, High Value": {"name": "Infrequent High-Tier Buyers"},
    "Moderate, Rare, Medium Value": {"name": "Dormant Trials"},
    "Moderate, Rare, Low Value": {"name": "Stalled Trials"},
    "Moderate, Rare, Very Low Value": {"name": "Negligible Leads"},

    # --- LAPSING ---
    "Lapsing, Very Frequent, Very High Value": {"name": "Critical At-Risk VIPs"},
    "Lapsing, Very Frequent, High Value": {"name": "At-Risk VIPs"},
    "Lapsing, Very Frequent, Medium Value": {"name": "Slowing High-Volume Accounts"},
    "Lapsing, Very Frequent, Low Value": {"name": "Departing Frequency Shoppers"},
    "Lapsing, Very Frequent, Very Low Value": {"name": "Fading Micro-Volume Users"},
    
    "Lapsing, Frequent, Very High Value": {"name": "Priority Re-engagement Targets"},
    "Lapsing, Frequent, High Value": {"name": "Slowing Loyals"},
    "Lapsing, Frequent, Medium Value": {"name": "Drifting Regulars"},
    "Lapsing, Frequent, Low Value": {"name": "Fading Bargain Shoppers"},
    "Lapsing, Frequent, Very Low Value": {"name": "Drifting Low-Tier Regulars"},
    
    "Lapsing, Occasional, Very High Value": {"name": "Slowing Big Spenders"},
    "Lapsing, Occasional, High Value": {"name": "Cooling Premium Shoppers"},
    "Lapsing, Occasional, Medium Value": {"name": "Cooling Mid-Tier Shoppers"},
    "Lapsing, Occasional, Low Value": {"name": "Drifting Casuals"},
    "Lapsing, Occasional, Very Low Value": {"name": "Neglected Contacts"},
    
    "Lapsing, Infrequent, Very High Value": {"name": "At-Risk Whale Accounts"},
    "Lapsing, Infrequent, High Value": {"name": "Detached Premium Accounts"},
    "Lapsing, Infrequent, Medium Value": {"name": "Slowing Occasionals"},
    "Lapsing, Infrequent, Low Value": {"name": "Unresponsive Leads"},
    "Lapsing, Infrequent, Very Low Value": {"name": "Leaving Low-Value Accounts"},
    
    "Lapsing, Rare, Very High Value": {"name": "Dormant Luxury Accounts"},
    "Lapsing, Rare, High Value": {"name": "Dormant High-Value Contacts"},
    "Lapsing, Rare, Medium Value": {"name": "Fading Single-Buyers"},
    "Lapsing, Rare, Low Value": {"name": "Inactive Casuals"},
    "Lapsing, Rare, Very Low Value": {"name": "Cold Prospects"},

    # --- LAPSED ---
    "Lapsed, Very Frequent, Very High Value": {"name": "Lost High-Value Legends"},
    "Lapsed, Very Frequent, High Value": {"name": "Lost Advocates"},
    "Lapsed, Very Frequent, Medium Value": {"name": "Lost Volume Accounts"},
    "Lapsed, Very Frequent, Low Value": {"name": "Abandoned Repeaters"},
    "Lapsed, Very Frequent, Very Low Value": {"name": "Abandoned Micro-Users"},
    
    "Lapsed, Frequent, Very High Value": {"name": "Lost VIPs"},
    "Lapsed, Frequent, High Value": {"name": "Former Loyals"},
    "Lapsed, Frequent, Medium Value": {"name": "Lost Mid-Tier Regulars"},
    "Lapsed, Frequent, Low Value": {"name": "Churned Regulars"},
    "Lapsed, Frequent, Very Low Value": {"name": "Churned Low-Tier Regulars"},
    
    "Lapsed, Occasional, Very High Value": {"name": "Lost High-Value Splurgers"},
    "Lapsed, Occasional, High Value": {"name": "Lost High-Tier Casuals"},
    "Lapsed, Occasional, Medium Value": {"name": "Lost Mid-Tier Casuals"},
    "Lapsed, Occasional, Low Value": {"name": "Inactive Casual Shoppers"},
    "Lapsed, Occasional, Very Low Value": {"name": "Zero-Engagement Accounts"},
    
    "Lapsed, Infrequent, Very High Value": {"name": "Lost One-Time Whales"},
    "Lapsed, Infrequent, High Value": {"name": "Lost High-Value Contacts"},
    "Lapsed, Infrequent, Medium Value": {"name": "Lost Mid-Tier Accounts"},
    "Lapsed, Infrequent, Low Value": {"name": "Lost Accounts"},
    "Lapsed, Infrequent, Very Low Value": {"name": "Dead Leads"},
    
    "Lapsed, Rare, Very High Value": {"name": "Historical Luxury Sign-ups"},
    "Lapsed, Rare, High Value": {"name": "Historical High-Value Sign-ups"},
    "Lapsed, Rare, Medium Value": {"name": "Historical Mid-Tier Sign-ups"},
    "Lapsed, Rare, Low Value": {"name": "Historical Low-Value Sign-ups"},
    "Lapsed, Rare, Very Low Value": {"name": "Defunct Leads"}
}
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

kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
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

cluster_counts['Type'] = cluster_counts['Label'].apply(lambda x: customer_segments.get(x, {}).get("name", f"Custom Segment ({x})"))

pfig = px.pie(
        cluster_counts, 
        names='Type', 
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
top_customers['Type'] = top_customers['Label'].apply(lambda x: customer_segments[x]['name'])
st.dataframe(top_customers[["CustomerID", "Total_Price_LKR", "Type"]].reset_index(drop=True))

st.markdown("* Customer segments definitions")
st.dataframe(cluster_counts[['Type', 'Label']])