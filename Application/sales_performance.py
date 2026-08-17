import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import geopandas as gpd
import matplotlib.pylab as plt
import matplotlib.colors as mcolors
from utils import get_raw_data, clean_data, get_sales_forecast

st.markdown("# Sales Performance Analysis")
st.caption("Transactions are aggregated by year, seasonal timing patterns, product lines and districts to evaluate overall revenue performance. Future predictions are generated using a Random Forest Regressor model")

raw_df, is_uploaded = get_raw_data()
st.set_page_config(page_title="Sales Performance")

# st.sidebar.markdown(
#     "*Currently using uploaded file.*" if is_uploaded
#     else "*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*"
# )

df = clean_data(raw_df)

COLOR_PRIMARY = "#5E81AC"        
COLOR_ACCENT = "#D08770"         
COLOR_TERTIARY = "#B48EAD"       

COLOR_SEQUENTIAL = ['#D8DEE9', '#B48EAD', '#BF616A', '#EBCB8B', '#A3BE8C', '#88C0D0', '#5E81AC']

CHOROPLETH_SHADES = ['#ECEFF4', '#D8DEE9', '#C8D3E0', '#A9C2D4', '#8FBCBB',
                      '#81A1C1', '#5E81AC', '#4C6A92', '#3B4252']
CHOROPLETH_CMAP = mcolors.LinearSegmentedColormap.from_list("nord_frost", CHOROPLETH_SHADES)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# TABBED SECTIONS
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Revenue Trends", "Forecast", "Timing Patterns", "Top Products", "District Distribution"]
)

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

# --- TAB 2: FORECAST ---
with tab2:
    st.markdown("### Annual Sales Forecast")

    NORD_ACTUAL = "#A3BE8C"     
    NORD_FORECAST = COLOR_PRIMARY  

    history_recent, forecast_dataset, combined, forecast_summary_md, peak_period, best_model = \
        get_sales_forecast(df, is_uploaded)

    st.caption(
        f"Comparing the previous year (**{history_recent['Year_Label'].iloc[0]}**, actual) against "
        f"the model's forecast for the **next year** "
        f"(**{forecast_dataset['Year_Label'].iloc[0]}**). "
        f"Projected peak month: **{peak_period['Date'].strftime('%b %Y')}** at **{peak_period['Sales']:.2f}M LKR**."
    )
    if is_uploaded:
        st.caption(f"Model (tuned via grid search on your data): *{best_model}*")
    else:
        st.caption("Model: *RandomForestRegressor (pre-tuned for the demo dataset)*")

    boundary_date = history_recent["Date"].max()

    # Actual (previous year)
    actual_area = (
        alt.Chart(history_recent)
        .mark_area(
            interpolate='monotone', line=False,
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color=NORD_ACTUAL, offset=0),
                       alt.GradientStop(color='rgba(163,190,140,0)', offset=1)],
                x1=1, x2=1, y1=1, y2=0,
            ),
        )
        .encode(x=alt.X('Date:T', title='Month', axis=alt.Axis(format='%b %Y')),
                y=alt.Y('Sales:Q', title='Revenue (M LKR)'))
    )
    actual_line = (
        alt.Chart(history_recent)
        .mark_line(interpolate='monotone', color=NORD_ACTUAL, strokeWidth=3)
        .encode(x=alt.X('Date:T'), y=alt.Y('Sales:Q'))
    )
    actual_points = (
        alt.Chart(history_recent)
        .mark_point(filled=True, size=80, color=NORD_ACTUAL)
        .encode(
            x=alt.X('Date:T'), y=alt.Y('Sales:Q'),
            tooltip=[alt.Tooltip('Date:T', title='Month', format='%b %Y'),
                     alt.Tooltip('Quarter_Label:N', title='Quarter'),
                     alt.Tooltip('Sales:Q', title='Actual Revenue (M LKR)', format=',.2f')],
        )
    )

    # Forecast (next year)
    forecast_area = (
        alt.Chart(forecast_dataset)
        .mark_area(
            interpolate='monotone', line=False,
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color=NORD_FORECAST, offset=0),
                       alt.GradientStop(color='rgba(94,129,172,0)', offset=1)],
                x1=1, x2=1, y1=1, y2=0,
            ),
        )
        .encode(x=alt.X('Date:T'), y=alt.Y('Sales:Q'))
    )
    forecast_line = (
        alt.Chart(forecast_dataset)
        .mark_line(interpolate='monotone', color=NORD_FORECAST, strokeWidth=3, strokeDash=[6, 3])
        .encode(x=alt.X('Date:T'), y=alt.Y('Sales:Q'))
    )
    forecast_points = (
        alt.Chart(forecast_dataset)
        .mark_point(filled=True, size=80, color=NORD_FORECAST)
        .encode(
            x=alt.X('Date:T'), y=alt.Y('Sales:Q'),
            tooltip=[alt.Tooltip('Date:T', title='Month', format='%b %Y'),
                     alt.Tooltip('Quarter_Label:N', title='Quarter'),
                     alt.Tooltip('Sales:Q', title='Forecasted Revenue (M LKR)', format=',.2f')],
        )
    )

    peak_forecast_label = (
        alt.Chart(pd.DataFrame([peak_period]))
        .mark_text(dy=-16, fontSize=12, fontWeight='bold', color='#ECEFF4')
        .encode(x=alt.X('Date:T'), y=alt.Y('Sales:Q'), text=alt.Text('Sales:Q', format=',.2f'))
    )

    # Dashed vertical rule marking where actuals end and the forecast begins
    boundary_rule = (
        alt.Chart(pd.DataFrame({'Date': [boundary_date]}))
        .mark_rule(strokeDash=[4, 4], color='#A9B4C4', strokeWidth=1.5)
        .encode(x=alt.X('Date:T'))
    )

    quarter_starts = (
        forecast_dataset.groupby('Quarter_Label', sort=False)['Date'].min().reset_index()
    )
    quarter_dividers = (
        alt.Chart(quarter_starts)
        .mark_rule(strokeDash=[2, 3], color='#4C566A', strokeWidth=1)
        .encode(x=alt.X('Date:T'))
    )
    quarter_labels = (
        alt.Chart(quarter_starts)
        .mark_text(dy=-160, fontSize=11, color='#A9B4C4', align='left', dx=4)
        .encode(x=alt.X('Date:T'), text=alt.Text('Quarter_Label:N'))
    )

    st.altair_chart(
        (actual_area + forecast_area + actual_line + forecast_line
         + actual_points + forecast_points + boundary_rule
         + quarter_dividers + quarter_labels + peak_forecast_label)
        .properties(height=380)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=True, gridOpacity=0.08),
        use_container_width=True
    )

    lcol1, lcol2 = st.columns(2)
    with lcol1:
        st.markdown(
            f"<span style='color:{NORD_ACTUAL};'>●</span>&nbsp; "
            f"Actual — Previous Year ({history_recent['Year_Label'].iloc[0]})",
            unsafe_allow_html=True
        )
    with lcol2:
        st.markdown(
            f"<span style='color:{NORD_FORECAST};'>●&#8212;</span>&nbsp; "
            f"Forecast — Next Year ({forecast_dataset['Year_Label'].iloc[0]})",
            unsafe_allow_html=True
        )

# --- TAB 3: TIMING PATTERNS ---
with tab3:
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
                scale=alt.Scale(range=['#F4DBD6', COLOR_ACCENT, '#3B4252']),
            ),
            tooltip=[alt.Tooltip('Day:N', title='Day'),
                     alt.Tooltip('Hour:O', title='Hour'),
                     alt.Tooltip('Total_Price_LKR:Q', title='Revenue (M LKR)', format=',.2f')],
        )
        .properties(height=280)
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(heatmap, use_container_width=True)

# --- TAB 4: TOP PRODUCTS ---
with tab4:
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

# --- TAB 5: DISTRICT DISTRIBUTION ---
with tab5:
    st.markdown("*This heat map and bar chart represent the districtwise distribution of total revenue.*")

    geo_data = gpd.read_file("https://raw.githubusercontent.com/dulnith-liyanage/RetailRadar/refs/heads/main/data/geodata/District_geo.json")
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