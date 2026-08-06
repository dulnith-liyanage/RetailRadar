import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import geopandas as gpd
import matplotlib.pylab as plt
import matplotlib.colors as mcolors
from utils import get_raw_data, clean_data

st.set_page_config(page_title="Sales Performance Analysis", page_icon="📈")

st.markdown("# Sales Performance Analysis")
st.caption("Transactions are aggregated by year, seasonal timing patterns, product lines and districts to evaluate overall revenue performance.")

raw_df, is_uploaded = get_raw_data()
st.sidebar.markdown(
    "*Currently using uploaded file.*" if is_uploaded
    else "*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*"
)

df = clean_data(raw_df)

# ============================================================
# COLOR PALETTE — Nord, used consistently across every chart
# ============================================================
COLOR_PRIMARY = "#5E81AC"        # Nord Frost (Blue) — revenue metrics
COLOR_ACCENT = "#D08770"         # Nord Aurora (Orange) — timing / behavioral charts
COLOR_TERTIARY = "#B48EAD"       # Nord Aurora (Purple) — secondary product metric

# Nord pastel set for multi-category charts (donut, grouped bars)
# Snow Storm, Purple, Red, Yellow, Green, Frost(Sky), Frost(Blue)
COLOR_SEQUENTIAL = ['#D8DEE9', '#B48EAD', '#BF616A', '#EBCB8B', '#A3BE8C', '#88C0D0', '#5E81AC']

# Sequential gradient for the district choropleth, derived from Nord's Frost/Polar Night
# family — Snow Storm through Frost Blue down into Polar Night for the darkest values
CHOROPLETH_SHADES = ['#ECEFF4', '#D8DEE9', '#C8D3E0', '#A9C2D4', '#8FBCBB',
                      '#81A1C1', '#5E81AC', '#4C6A92', '#3B4252']
CHOROPLETH_CMAP = mcolors.LinearSegmentedColormap.from_list("nord_frost", CHOROPLETH_SHADES)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# ============================================================
# TABBED SECTIONS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["Revenue Trends", "Timing Patterns", "Top Products", "District Distribution"])

# --- TAB 1: REVENUE TRENDS ---
with tab1:
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    col1, col2 = st.columns(2, gap='large')

    with col1:
        st.markdown("### Total Revenue by Year")

        year_data = df.groupby('Year')['Total_Price_LKR'].sum().reset_index()
        year_data['Total_Price_LKR'] = year_data['Total_Price_LKR'] / 1000000
        year_data = year_data.sort_values('Year')
        year_data['Year'] = year_data['Year'].astype(str)
        year_order = year_data['Year'].tolist()

        total_revenue_value = year_data['Total_Price_LKR'].sum()
        total_text = f"{total_revenue_value:.1f} M LKR"

        fig = px.pie(
            year_data,
            names='Year',
            values='Total_Price_LKR',
            hole=0.7,
            category_orders={'Year': year_order},
            color_discrete_sequence=COLOR_SEQUENTIAL
        )

        fig.update_layout(
            annotations=[
                dict(text='TOTAL REVENUE', x=0.5, y=0.54, font_size=13, showarrow=False, font_color="#a0aab8",),
                dict(text=total_text, x=0.5, y=0.49, font_size=20, showarrow=False, font_color="white")
            ],
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                title=None
            ),
            showlegend=True,
            margin=dict(t=20, b=20, l=20, r=20)
        )

        fig.update_traces(
            textinfo='none',
            marker=dict(line=dict(color='#2E3440', width=4)),  # Nord Polar Night — matches dashboard background
            hovertemplate="%{label}<br>%{value:.1f}M LKR (%{percent})<extra></extra>",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Total Revenue by Month")
        monthly_revenue_only = df.groupby('Month')['Total_Price_LKR'].sum().reset_index()
        monthly_revenue_only['Total_Price_LKR'] = monthly_revenue_only['Total_Price_LKR'] / 1000000
        monthly_revenue_only = monthly_revenue_only.sort_values('Month')
        monthly_revenue_only['Month_Name'] = monthly_revenue_only['Month'].apply(lambda m: month_names[m - 1])

        st.altair_chart(
            alt.Chart(monthly_revenue_only)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X('Month_Name:N', sort=month_names, title='Month'),
                y=alt.Y('Total_Price_LKR:Q', title='Total Revenue in Million LKR'),
                color=alt.Color(
                    'Total_Price_LKR:Q',
                    scale=alt.Scale(range=['#4C6A92', COLOR_PRIMARY, '#A9C2D4']),
                    legend=None,
                ),
                tooltip=[alt.Tooltip('Month_Name:N', title='Month'),
                         alt.Tooltip('Total_Price_LKR:Q', title='Revenue (M LKR)', format=',.2f')],
            )
            .properties(height=320)
            .configure_view(strokeWidth=0)
            .configure_axis(grid=True, gridOpacity=0.08),
            use_container_width=True
        )

    st.markdown("### Total Revenue by Year and Month")
    monthly_revenue = df.groupby(['Year', 'Month'])['Total_Price_LKR'].sum().reset_index()
    monthly_revenue['Total_Price_LKR'] = monthly_revenue['Total_Price_LKR'] / 1000000
    monthly_revenue['Year'] = monthly_revenue['Year'].astype(str)
    monthly_revenue['Month_Name'] = monthly_revenue['Month'].apply(lambda m: month_names[m - 1])

    st.altair_chart(
        alt.Chart(monthly_revenue)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X('Month_Name:N', title='Month', sort=month_names),
            y=alt.Y('Total_Price_LKR:Q', title='Total Revenue in Million LKR'),
            color=alt.Color('Year:N', scale=alt.Scale(domain=year_order, range=COLOR_SEQUENTIAL), title='Year'),
            xOffset=alt.XOffset('Year:N', sort=year_order),
            tooltip=[alt.Tooltip('Year:N'), alt.Tooltip('Month_Name:N', title='Month'),
                     alt.Tooltip('Total_Price_LKR:Q', title='Revenue (M LKR)', format=',.2f')],
        )
        .properties(height=360)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=True, gridOpacity=0.08),
        use_container_width=True
    )

# --- TAB 2: TIMING PATTERNS ---
with tab2:
    col3, col4 = st.columns(2, gap='large')

    with col3:
        st.markdown("### Weekly Revenue Trend")
        weekly_sales = df.groupby("Day")["Total_Price_LKR"].sum().reset_index()
        weekly_sales["Total_Price_LKR"] = weekly_sales["Total_Price_LKR"] / 1000000
        weekly_sales['Day'] = pd.Categorical(weekly_sales['Day'], categories=day_order, ordered=True)
        weekly_sales = weekly_sales.sort_values('Day').reset_index(drop=True)

        peak_day = weekly_sales.loc[weekly_sales['Total_Price_LKR'].idxmax()]
        st.caption(f"Peak day: **{peak_day['Day']}** at {peak_day['Total_Price_LKR']:.1f}M LKR")

        weekly_area = (
            alt.Chart(weekly_sales)
            .mark_area(
                interpolate='monotone', line=False,
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color=COLOR_ACCENT, offset=0),
                           alt.GradientStop(color='rgba(208,135,127,0)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0,
                ),
            )
            .encode(x=alt.X('Day:N', sort=day_order, title=None),
                    y=alt.Y('Total_Price_LKR:Q', title='Total Revenue in Million LKR'))
        )

        weekly_line = (
            alt.Chart(weekly_sales)
            .mark_line(interpolate='monotone', color=COLOR_ACCENT, strokeWidth=3)
            .encode(x=alt.X('Day:N', sort=day_order), y=alt.Y('Total_Price_LKR:Q'))
        )

        weekly_points = (
            alt.Chart(weekly_sales)
            .mark_point(filled=True, size=90, color=COLOR_ACCENT)
            .encode(
                x=alt.X('Day:N', sort=day_order),
                y=alt.Y('Total_Price_LKR:Q'),
                tooltip=[alt.Tooltip('Day:N', title='Day'),
                         alt.Tooltip('Total_Price_LKR:Q', title='Revenue (M LKR)', format=',.2f')],
            )
        )

        weekly_peak_label = (
            alt.Chart(pd.DataFrame([peak_day]))
            .mark_text(dy=-16, fontSize=12, fontWeight='bold', color='#ECEFF4')
            .encode(x=alt.X('Day:N', sort=day_order), y=alt.Y('Total_Price_LKR:Q'),
                    text=alt.Text('Total_Price_LKR:Q', format=',.1f'))
        )

        st.altair_chart(
            (weekly_area + weekly_line + weekly_points + weekly_peak_label)
            .properties(height=340)
            .configure_view(strokeWidth=0)
            .configure_axis(grid=True, gridOpacity=0.08),
            use_container_width=True
        )

    with col4:
        st.markdown("### Hourly Revenue Trend")
        hourly_sales = df.groupby('Hour')['Total_Price_LKR'].sum().reset_index()
        hourly_sales['Total_Price_LKR'] = hourly_sales['Total_Price_LKR'] / 1000000
        hourly_sales = hourly_sales.sort_values('Hour').reset_index(drop=True)

        peak_hour = hourly_sales.loc[hourly_sales['Total_Price_LKR'].idxmax()]
        st.caption(f"Peak hour: **{int(peak_hour['Hour']):02d}:00** at {peak_hour['Total_Price_LKR']:.1f}M LKR")

        hourly_area = (
            alt.Chart(hourly_sales)
            .mark_area(
                interpolate='monotone', line=False,
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color=COLOR_PRIMARY, offset=0),
                           alt.GradientStop(color='rgba(94,129,172,0)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0,
                ),
            )
            .encode(x=alt.X('Hour:O', title='Hour of Day', axis=alt.Axis(labelExpr="datum.value + ':00'")),
                    y=alt.Y('Total_Price_LKR:Q', title='Total Revenue in Million LKR'))
        )

        hourly_line = (
            alt.Chart(hourly_sales)
            .mark_line(interpolate='monotone', color=COLOR_PRIMARY, strokeWidth=3)
            .encode(x=alt.X('Hour:O'), y=alt.Y('Total_Price_LKR:Q'))
        )

        hourly_points = (
            alt.Chart(hourly_sales)
            .mark_point(filled=True, size=90, color=COLOR_PRIMARY)
            .encode(
                x=alt.X('Hour:O'),
                y=alt.Y('Total_Price_LKR:Q'),
                tooltip=[alt.Tooltip('Hour:O', title='Hour'),
                         alt.Tooltip('Total_Price_LKR:Q', title='Revenue (M LKR)', format=',.2f')],
            )
        )

        hourly_peak_label = (
            alt.Chart(pd.DataFrame([peak_hour]))
            .mark_text(dy=-16, fontSize=12, fontWeight='bold', color='#ECEFF4')
            .encode(x=alt.X('Hour:O'), y=alt.Y('Total_Price_LKR:Q'),
                    text=alt.Text('Total_Price_LKR:Q', format=',.1f'))
        )

        st.altair_chart(
            (hourly_area + hourly_line + hourly_points + hourly_peak_label)
            .properties(height=340)
            .configure_view(strokeWidth=0)
            .configure_axis(grid=True, gridOpacity=0.08),
            use_container_width=True
        )

    st.markdown("### Revenue Heatmap: Day × Hour")
    st.caption("Darker cells mark the busiest day-hour combinations — useful for staffing and promotion timing.")

    heatmap_data = df.groupby(['Day', 'Hour'])['Total_Price_LKR'].sum().reset_index()
    heatmap_data['Total_Price_LKR'] = heatmap_data['Total_Price_LKR'] / 1000000
    heatmap_data['Day'] = pd.Categorical(heatmap_data['Day'], categories=day_order, ordered=True)

    heatmap = (
        alt.Chart(heatmap_data)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X('Hour:O', title='Hour of Day', axis=alt.Axis(labelExpr="datum.value + ':00'")),
            y=alt.Y('Day:N', sort=day_order, title=None),
            color=alt.Color(
                'Total_Price_LKR:Q',
                title='Revenue (M LKR)',
                scale=alt.Scale(range=['#3B4252', COLOR_ACCENT, '#F4DBD6']),
            ),
            tooltip=[alt.Tooltip('Day:N', title='Day'),
                     alt.Tooltip('Hour:O', title='Hour'),
                     alt.Tooltip('Total_Price_LKR:Q', title='Revenue (M LKR)', format=',.2f')],
        )
        .properties(height=280)
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(heatmap, use_container_width=True)

# --- TAB 3: TOP PRODUCTS ---
with tab3:
    st.markdown("### Top 10 Products by Revenue")
    top_products = df.groupby('Description')['Total_Price_LKR'].sum().sort_values(ascending=False).head(10).reset_index()
    top_products['Total_Price_LKR'] = top_products['Total_Price_LKR'] / 1000000
    st.caption(f"These 10 products together generated {top_products['Total_Price_LKR'].sum():,.1f}M LKR.")

    revenue_bars = (
        alt.Chart(top_products)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, height=18)
        .encode(
            y=alt.Y('Description', sort='-x', axis=alt.Axis(labelLimit=300), title=None),
            x=alt.X('Total_Price_LKR', title='Total Revenue in Million LKR',
                     axis=alt.Axis(format=',.1f')),
            color=alt.Color(
                'Total_Price_LKR:Q',
                scale=alt.Scale(range=['#4C6A92', COLOR_PRIMARY, '#A9C2D4']),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip('Description:N', title='Product'),
                alt.Tooltip('Total_Price_LKR:Q', title='Revenue (M LKR)', format=',.2f'),
            ],
        )
    )

    revenue_labels = (
        alt.Chart(top_products)
        .mark_text(align='left', dx=5, color='#ECEFF4', fontSize=11)
        .encode(
            y=alt.Y('Description', sort='-x'),
            x=alt.X('Total_Price_LKR'),
            text=alt.Text('Total_Price_LKR:Q', format=',.2f'),
        )
    )

    st.altair_chart(
        (revenue_bars + revenue_labels).properties(height=380).configure_view(strokeWidth=0),
        use_container_width=True
    )

    st.markdown("### Top 10 Products by Sold Quantity")
    top_products_by_q = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10).reset_index()
    st.caption(f"These 10 products together sold {top_products_by_q['Quantity'].sum():,.0f} units.")

    quantity_bars = (
        alt.Chart(top_products_by_q)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, height=18)
        .encode(
            y=alt.Y('Description', sort='-x', axis=alt.Axis(labelLimit=300), title=None),
            x=alt.X('Quantity', title='Sold Quantity', axis=alt.Axis(format=',d')),
            color=alt.Color(
                'Quantity:Q',
                scale=alt.Scale(range=['#4C3B52', COLOR_TERTIARY, '#E3D3F0']),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip('Description:N', title='Product'),
                alt.Tooltip('Quantity:Q', title='Units Sold', format=',d'),
            ],
        )
    )

    quantity_labels = (
        alt.Chart(top_products_by_q)
        .mark_text(align='left', dx=5, color='#ECEFF4', fontSize=11)
        .encode(
            y=alt.Y('Description', sort='-x'),
            x=alt.X('Quantity'),
            text=alt.Text('Quantity:Q', format=',d'),
        )
    )

    st.altair_chart(
        (quantity_bars + quantity_labels).properties(height=380).configure_view(strokeWidth=0),
        use_container_width=True
    )

# --- TAB 4: DISTRICT DISTRIBUTION ---
with tab4:
    st.markdown("*This heat map and bar chart represent the districtwise distribution of total revenue.*")

    geo_data = gpd.read_file("../data/geodata/District_geo.json")
    geo_data = geo_data[['ADM2_EN', 'geometry']].rename(columns={'ADM2_EN': 'District'})

    dis_df = df.groupby('District')['Total_Price_LKR'].sum().sort_values(ascending=False).reset_index()
    district = geo_data.merge(dis_df, how='left', left_on='District', right_on='District')
    district = district.iloc[1:]

    district["Total_Price_LKR"] = district["Total_Price_LKR"] / 1000000  # Convert to millions

    colA, colB = st.columns(2, gap='large')

    with colA:
        fig, ax = plt.subplots(figsize=(5, 5))
        district.plot(column='Total_Price_LKR', cmap=CHOROPLETH_CMAP, ax=ax, legend=False,
                       missing_kwds={"color": "white", "label": "No data"})
        ax.axis('off')
        st.pyplot(fig, use_container_width=False, transparent=True)

    with colB:
        st.write("")
        st.write("")
        chart = (
            alt.Chart(district)
            .mark_bar()
            .encode(
                y=alt.Y('District', sort='-x'),
                x=alt.X('Total_Price_LKR', title='Total Revenue in Million LKR'),
                color=alt.Color('Total_Price_LKR', scale=alt.Scale(range=CHOROPLETH_SHADES), legend=None),
            )
        )

        st.altair_chart(chart, use_container_width=False)