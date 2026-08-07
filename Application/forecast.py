import streamlit as st
import pandas as pd
import altair as alt
from sklearn.model_selection import  GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from utils import get_raw_data, clean_data

raw_df, is_uploaded = get_raw_data()
df = clean_data(raw_df)

st.sidebar.markdown(
    "*Currently using uploaded file.*" if is_uploaded
    else "*Currently using the demo file. You can analyze your own files by uploading them in welcome page.*"
)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
daily_sales = df.groupby(["InvoiceDate"])["Total_Price_LKR"].sum().reset_index()

daily_sales["day"] = daily_sales["InvoiceDate"].dt.day
daily_sales["month"] = daily_sales["InvoiceDate"].dt.month
daily_sales["year"] = daily_sales["InvoiceDate"].dt.year
daily_sales["dayofweek"] = daily_sales["InvoiceDate"].dt.dayofweek


X = daily_sales[["year", "day", "month", "dayofweek"]]
y = daily_sales["Total_Price_LKR"]


#forecast 30 days starting from final day in dataset
last_date = daily_sales["InvoiceDate"].iloc[-1]

future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30, freq='D')

X_forecast = pd.DataFrame({
    "year": future_dates.year,
    "day": future_dates.day,
    "month": future_dates.month,
    "dayofweek": future_dates.dayofweek
})

if is_uploaded:
    reg = RandomForestRegressor(
        random_state=42
    )

    param_grid = {
        'n_estimators': [100, 200],          # Number of trees
        'max_depth': [None, 10, 20],         # Tree depth
        'min_samples_split': [2, 5],         # Min samples to split a node
        'min_samples_leaf': [1, 2],          # Min samples at a leaf
        'max_features': ['sqrt', 'log2']     # Features considered at each split
    }

    grid_search = GridSearchCV(
        param_grid=param_grid,
        estimator=reg,
        cv=5,
        scoring='neg_mean_squared_error',  # Optimize for MSE
        n_jobs=-1,                 # Use all CPU cores
        verbose=2
    )

    grid_search.fit(X, y)
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_forecast)
    st.sidebar.markdown(f"Model: *{best_model}*")
    
else:
    #Using the best model for the demo dataset
    best_model = RandomForestRegressor(max_depth=10, max_features='sqrt', min_samples_leaf=2, min_samples_split=5, n_estimators=200, random_state=42)
    best_model.fit(X, y)
    y_pred = best_model.predict(X_forecast)

forecast_dataset = pd.DataFrame({
    "Date": future_dates.date,
    "Sales": y_pred
})

forecast_dataset["Sales"] = forecast_dataset["Sales"] / 1000000
peak_day = forecast_dataset.loc[forecast_dataset["Sales"].idxmax()]

st.markdown("### 30 Days sales forecast")
st.caption(f"Projected peak: **{peak_day['Date'].strftime('%b %d')}** at **{peak_day['Sales']:.1f}M LKR**")

forecast_area = (
    alt.Chart(forecast_dataset)
    .mark_area(
        interpolate='monotone', line=False,
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='#5E81AC', offset=0),
                   alt.GradientStop(color='rgba(94,129,172,0)', offset=1)],
            x1=1, x2=1, y1=1, y2=0,
        ),
    )
    .encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Sales:Q', title='Forecasted Revenue (M LKR)')
    )
)

forecast_line = (
    alt.Chart(forecast_dataset)
    .mark_line(interpolate='monotone', color='#5E81AC', strokeWidth=3)
    .encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Sales:Q')
    )
)

forecast_points = (
    alt.Chart(forecast_dataset)
    .mark_point(filled=True, size=90, color='#5E81AC')
    .encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Sales:Q'),
        tooltip=[alt.Tooltip('Date:T', title='Date', format='%b %d, %Y'),
                 alt.Tooltip('Sales:Q', title='Revenue (M LKR)', format=',.2f')],
    )
)

peak_label = (
    alt.Chart(pd.DataFrame([peak_day]))
    .mark_text(dy=-16, fontSize=12, fontWeight='bold', color='#ECEFF4')
    .encode(
        x=alt.X('Date:T'),
        y=alt.Y('Sales:Q'),
        text=alt.Text('Sales:Q', format=',.1f')
    )
)

st.altair_chart(
    (forecast_area + forecast_line + forecast_points + peak_label)
    .properties(height=340)
    .configure_view(strokeWidth=0)
    .configure_axis(grid=True, gridOpacity=0.08),
    use_container_width=True
)
