from utils import get_raw_data, clean_data, get_segment_summary
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

NORD_SEQUENTIAL = ['#D8DEE9', '#B48EAD', '#BF616A', '#EBCB8B', '#A3BE8C', '#88C0D0', '#5E81AC']
NORD_BG = "#2E3440"          
NORD_CARD_BG = "#3B4252"     
NORD_TEXT_MUTED = "#A9B4C4"  
NORD_FROST = "#88C0D0"
NORD_FROST_DEEP = "#5E81AC"

raw_df, is_uploaded = get_raw_data()
st.set_page_config(page_title="Customer Segments")

# st.sidebar.markdown(
#     "*Currently using uploaded file.*" if is_uploaded
#     else "*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*"
# )

st.markdown("# Customer Segmentation")
st.caption("Customers are grouped using RFM (Recency, Frequency, Monetary) analysis and K-Means clustering into behavioral segments.")

df = clean_data(raw_df)

st.sidebar.markdown("### Clustering Settings")
num_clusters = st.sidebar.slider("Number of Segments (K)", min_value=2, max_value=12, value=6, step=1)

# RFM + K-Means Clustering 
customers, cluster_counts, segment_summary_md, silhouette_score = get_segment_summary(df, n_clusters=num_clusters)
st.sidebar.metric("Clustering Score (Silhouette)", f"{silhouette_score:.3f}")


# Segment icon helper
def segment_icon(segment_type: str) -> str:
    t = segment_type.lower()
    if any(k in t for k in ["champion", "vip", "legend"]):
        return "🏆"
    if any(k in t for k in ["whale", "premium", "luxury", "high-value"]):
        return "💎"
    if any(k in t for k in ["lost", "churn", "dead", "defunct", "inactive", "cold", "dormant", "fading", "abandoned"]):
        return "⚠️"
    if any(k in t for k in ["risk", "slowing", "drifting", "cooling", "leaving", "detached", "unrealized", "unresponsive"]):
        return "🔻"
    if any(k in t for k in ["new", "trial", "starter", "newcomer", "prospect", "first-time", "sign-up", "onboard", "registration"]):
        return "✨"
    if any(k in t for k in ["loyal", "core", "regular", "mainstay", "advocate"]):
        return "💙"
    return "🔹"


cluster_counts = cluster_counts.copy()
cluster_counts["Icon"] = cluster_counts["Type"].apply(segment_icon)
cluster_counts["Type_Display"] = cluster_counts["Icon"] + " " + cluster_counts["Type"]
cluster_counts["R_Tier"] = cluster_counts["Label"].str.split(",").str[0].str.strip()

customers = customers.copy()
customers["R_Tier"] = customers["Label"].str.split(",").str[0].str.strip()

CHURN_TIERS = ["Lapsing", "Lapsed"]

unique_customer_count = customers["CustomerID"].nunique()

# TABBED SECTIONS
tab1, tab2, tab3, tab4 = st.tabs(["Segment Overview", "Top Customers", "Churning Customers", "Explore & Definitions"])

# --- TAB 1: SEGMENT OVERVIEW ---
with tab1:
    st.markdown("### Segment Composition")

    pie_data = cluster_counts.sort_values("Count", ascending=False).copy()
    pie_data["Pct"] = pie_data["Count"] / pie_data["Count"].sum() * 100
    pie_data["Legend_Label"] = (
        pie_data["Type_Display"] + " (" + pie_data["Count"].astype(str) + ")"
    )
    SMALL_SLICE_THRESHOLD = 8  # % share below which a slice gets pulled out
    pie_data["Pull"] = pie_data["Pct"].apply(lambda p: 0.09 if p < SMALL_SLICE_THRESHOLD else 0)

    pfig = px.pie(
        pie_data,
        names="Legend_Label",
        values="Count",
        hole=0.65,  # Turns the pie chart into a donut
        color_discrete_sequence=NORD_SEQUENTIAL,
    )
 
    # Style the central hole text, gaps between slices, and the horizontal legend
    pfig.update_layout(
        annotations=[
            dict(text="TOTAL UNIQUE CUSTOMERS", x=0.5, y=0.54, font_size=13, showarrow=False, font_color="#a0aab8"),
            dict(text=unique_customer_count, x=0.5, y=0.47, font_size=20, showarrow=False, font_color="white"),
        ],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            title=None,
            font=dict(size=12),
        ),
        showlegend=True,
        margin=dict(t=20, b=60, l=60, r=60),
    )

    pfig.update_traces(
        pull=pie_data["Pull"].tolist(),
        textinfo="percent",
        textposition="outside",
        texttemplate="%{percent:.1%}",
        textfont=dict(size=12, color="#D8DEE9"),
        marker=dict(line=dict(color=NORD_BG, width=3)),
        hovertemplate="%{label}<br>%{percent}<extra></extra>",
    )

    st.plotly_chart(pfig, use_container_width=True)
    st.caption("Small segments are pulled outward from the ring so they stay visible even at a low share of customers.")

    st.markdown("### Segment Landscape")
    st.caption("Bubble size = number of customers in the segment · position shows how large vs. how valuable each segment is.")

    landscape = px.scatter(
        cluster_counts,
        x="Count",
        y="Avg_Spend_LKR",
        size="Count",
        color="Type_Display",
        hover_name="Type_Display",
        hover_data={"Type_Display": False, "Count": True, "Avg_Spend_LKR": ":.1f", "Label": True},
        color_discrete_sequence=NORD_SEQUENTIAL,
        size_max=55,
        labels={"Count": "Number of Customers", "Avg_Spend_LKR": "Avg. Spend (Thousand LKR)"},
    )

    landscape.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5, title=None),
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor="rgba(236,239,244,0.08)"),
        yaxis=dict(gridcolor="rgba(236,239,244,0.08)"),
    )
    # sizemin guarantees even the smallest segment renders as a visible bubble,
    # not just a near-invisible dot
    landscape.update_traces(marker=dict(line=dict(color=NORD_BG, width=1.5), sizemin=8))

    st.plotly_chart(landscape, use_container_width=True)

# --- TAB 2: TOP CUSTOMERS ---
with tab2:
    st.markdown("### 🏆 Top 10 Customers by Total Amount Spent")

    top_customers = customers.sort_values(by="Total_Price_LKR", ascending=False).head(10).reset_index(drop=True)
    top_customers["Rank"] = top_customers.index + 1
    medal_map = {1: "🥇", 2: "🥈", 3: "🥉"}
    top_customers["Rank_Display"] = top_customers["Rank"].apply(lambda r: medal_map.get(r, f"#{r}"))
    top_customers["Segment"] = top_customers["Type"].apply(lambda t: f"{segment_icon(t)} {t}")
    top_customers["Total_Price_LKR_K"] = (top_customers["Total_Price_LKR"] / 1000).round(1)

    display_customers = top_customers[["Rank_Display", "CustomerID", "Segment", "Total_Price_LKR_K"]].rename(
        columns={"Rank_Display": "Rank", "Total_Price_LKR_K": "Total Spent (K LKR)"}
    )

    st.dataframe(
        display_customers,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Total Spent (K LKR)": st.column_config.ProgressColumn(
                "Total Spent (K LKR)",
                format="%.1f K",
                min_value=0,
                max_value=float(top_customers["Total_Price_LKR_K"].max()),
            ),
        },
    )

# --- TAB 3: CHURNING CUSTOMERS ---
with tab3:
    st.markdown("### 🚨 Churning Customers")
    st.caption("Customers whose recency has slipped into the **Lapsing** or **Lapsed** tiers — prioritize win-back outreach here.")

    churning_segments = cluster_counts[cluster_counts["R_Tier"].isin(CHURN_TIERS)].sort_values("Count", ascending=False)
    churning_customers = customers[customers["R_Tier"].isin(CHURN_TIERS)]

    if churning_customers.empty:
        st.success("No customers currently fall into the Lapsing or Lapsed recency tiers.")
    else:
        churn_count = churning_customers["CustomerID"].nunique()
        churn_pct = churn_count / unique_customer_count * 100
        revenue_at_risk_m = churning_customers["Total_Price_LKR"].sum() / 1_000_000

        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric("Customers at Risk", f"{churn_count:,}")
        with mcol2:
            st.metric("Share of Customer Base", f"{churn_pct:.1f}%")
        with mcol3:
            st.metric("Revenue at Risk", f"{revenue_at_risk_m:,.2f}M LKR")

        st.markdown("#### Churn Segments Breakdown")
        churn_chart = (
            alt.Chart(churning_segments)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                y=alt.Y("Type_Display:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
                x=alt.X("Count:Q", title="Customers"),
                color=alt.Color(
                    "Count:Q",
                    scale=alt.Scale(range=["#4C3B3E", "#BF616A", "#E8B4BA"]),
                    legend=None,
                ),
                tooltip=[
                    alt.Tooltip("Type:N", title="Segment"),
                    alt.Tooltip("R_Tier:N", title="Recency Tier"),
                    alt.Tooltip("Count:Q", title="Customers"),
                    alt.Tooltip("Avg_Spend_LKR:Q", title="Avg Spend (K LKR)", format=",.1f"),
                ],
            )
            .properties(height=max(180, 32 * len(churning_segments)))
        )
        st.altair_chart(churn_chart, use_container_width=True)

        st.markdown("#### Highest-Value Customers at Risk")
        st.caption("Sorted by total spend — these are the most valuable customers worth reaching out to first.")

        at_risk_top = churning_customers.sort_values("Total_Price_LKR", ascending=False).head(10).reset_index(drop=True)
        at_risk_top["Rank"] = at_risk_top.index + 1
        at_risk_top["Rank_Display"] = at_risk_top["Rank"].apply(lambda r: f"#{r}")
        at_risk_top["Segment"] = at_risk_top["Type"].apply(lambda t: f"{segment_icon(t)} {t}")
        at_risk_top["Total_Price_LKR_K"] = (at_risk_top["Total_Price_LKR"] / 1000).round(1)

        at_risk_display = at_risk_top[["Rank_Display", "CustomerID", "Segment", "R_Tier", "Total_Price_LKR_K"]].rename(
            columns={"Rank_Display": "Rank", "R_Tier": "Recency Tier", "Total_Price_LKR_K": "Total Spent (K LKR)"}
        )

        st.dataframe(
            at_risk_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Total Spent (K LKR)": st.column_config.ProgressColumn(
                    "Total Spent (K LKR)",
                    format="%.1f K",
                    min_value=0,
                    max_value=float(at_risk_top["Total_Price_LKR_K"].max()),
                ),
            },
        )

# --- TAB 4: EXPLORE & DEFINITIONS ---
with tab4:
    st.markdown("### 🔍 Explore a Segment")

    segment_options = cluster_counts.sort_values("Count", ascending=False)["Type"].tolist()
    selected_segments = st.multiselect(
        "Filter customers by segment",
        options=segment_options,
        default=[],
        format_func=lambda t: f"{segment_icon(t)} {t}",
    )

    if selected_segments:
        filtered = customers[customers["Type"].isin(selected_segments)].sort_values("Total_Price_LKR", ascending=False)
        filtered_display = filtered[["CustomerID", "Type", "Total_Price_LKR"]].copy()
        filtered_display["Segment"] = filtered_display["Type"].apply(lambda t: f"{segment_icon(t)} {t}")
        filtered_display["Total Spent (LKR)"] = filtered_display["Total_Price_LKR"].round(0)
        filtered_display = filtered_display[["CustomerID", "Segment", "Total Spent (LKR)"]]

        fcol1, fcol2 = st.columns(2)
        with fcol1:
            st.metric("Customers in selection", f"{filtered_display['CustomerID'].nunique():,}")
        with fcol2:
            st.metric("Combined spend", f"{filtered['Total_Price_LKR'].sum() / 1_000_000:,.2f}M LKR")

        st.dataframe(filtered_display, hide_index=True, use_container_width=True, height=300)
    else:
        st.caption("Select one or more segments above to list matching customers.")

    st.markdown("### Customer Segment Definitions")
    definitions = cluster_counts[["Type_Display", "Label", "Count", "Avg_Spend_LKR"]].rename(
        columns={
            "Type_Display": "Segment",
            "Label": "RFM Profile",
            "Count": "Customers",
            "Avg_Spend_LKR": "Avg. Spend (K LKR)",
        }
    ).sort_values("Customers", ascending=False)

    st.dataframe(definitions, hide_index=True, use_container_width=True)