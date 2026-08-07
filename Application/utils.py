import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def get_raw_data():
    if "dataset" in st.session_state:
        return st.session_state["dataset"], True
    return pd.read_csv("https://raw.githubusercontent.com/dulnith-liyanage/RetailRadar/refs/heads/main/data/output/srilanka_retail_2020_2026_small.csv"), False


@st.cache_data
def clean_data(df):
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.month
    df["Month_Name"] = df["InvoiceDate"].dt.month_name()
    df["Day"] = df["InvoiceDate"].dt.day_name()
    df["Hour"] = df["InvoiceDate"].dt.hour

    return df


# --- Shared RFM segment naming lookup ---
# (Trimmed here for brevity — paste your full customer_segments dict from rfm.py.
#  Keeping ONE copy of this dict, in utils.py, is the whole point of the refactor:
#  rfm.py and bot.py both import it instead of maintaining their own version.)
CUSTOMER_SEGMENTS = {
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

_recency_labels = ['Very Recent', 'Recent', 'Moderate', 'Lapsing', 'Lapsed']
_frequency_labels = ['Rare', 'Infrequent', 'Occasional', 'Frequent', 'Very Frequent']
_monetary_labels = ['Very Low Value', 'Low Value', 'Medium Value', 'High Value', 'Very High Value']


def _tier(value, bins, labels):
    for i, b in enumerate(bins):
        if value <= b:
            return labels[i]
    return labels[-1]


@st.cache_data
def get_segment_summary(df):
    """
    Runs RFM + K-Means clustering (same logic as rfm.py) and returns:
      - customers: per-customer dataframe with Cluster, Label, Type, Total_Price_LKR
      - cluster_counts: per-segment dataframe with Type, Label, Count, Avg_Spend_LKR
      - summary_md: a markdown table of cluster_counts, ready to drop into an LLM prompt
    """
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Quantity", "sum")
    ).reset_index()

    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[["Recency", "Frequency", "Monetary"]])

    kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(rfm_scaled)

    profile = rfm.groupby('Cluster')[['Recency', 'Frequency', 'Monetary']].mean().reset_index()

    r_bins = rfm['Recency'].quantile([0.2, 0.4, 0.6, 0.8]).values
    f_bins = rfm['Frequency'].quantile([0.2, 0.4, 0.6, 0.8]).values
    m_bins = rfm['Monetary'].quantile([0.2, 0.4, 0.6, 0.8]).values

    profile['R_Tier'] = profile['Recency'].apply(lambda v: _tier(v, r_bins, _recency_labels))
    profile['F_Tier'] = profile['Frequency'].apply(lambda v: _tier(v, f_bins, _frequency_labels))
    profile['M_Tier'] = profile['Monetary'].apply(lambda v: _tier(v, m_bins, _monetary_labels))
    profile['Label'] = profile['R_Tier'] + ", " + profile['F_Tier'] + ", " + profile['M_Tier']
    profile['Type'] = profile['Label'].apply(
        lambda x: CUSTOMER_SEGMENTS.get(x, {}).get("name", f"Custom Segment ({x})")
    )

    customers = profile.merge(rfm[['Cluster', 'CustomerID']], on='Cluster', how='left')
    customers = customers[["CustomerID", "Cluster", "Label", "Type"]]

    customer_total_spent = df.groupby("CustomerID")["Total_Price_LKR"].sum().reset_index()
    customers = customers.merge(customer_total_spent, on='CustomerID', how='left')

    cluster_counts = rfm['Cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Count']
    cluster_counts = cluster_counts.merge(profile[['Cluster', 'Type', 'Label']], on='Cluster', how='left')

    avg_spend = customers.groupby('Cluster')['Total_Price_LKR'].mean().reset_index()
    avg_spend.columns = ['Cluster', 'Avg_Spend_LKR']
    cluster_counts = cluster_counts.merge(avg_spend, on='Cluster', how='left')
    cluster_counts['Avg_Spend_LKR'] = (cluster_counts['Avg_Spend_LKR'] / 1000).round(1)  # in '000 LKR

    display_table = cluster_counts[['Type', 'Label', 'Count', 'Avg_Spend_LKR']].sort_values(
        by='Count', ascending=False
    ).rename(columns={'Avg_Spend_LKR': 'Avg_Spend_Thousand_LKR'})

    summary_md = display_table.to_markdown(index=False)

    return customers, cluster_counts, summary_md