"""Jamshedpur AirWatch - Streamlit dashboard."""

import streamlit as st

from dashboard.data_loader import load_gold_data
from dashboard.charts import (
    aqi_trend_chart,
    pollutant_chart,
    daily_aqi_category_chart,
)

st.set_page_config(
    page_title="Jamshedpur AirWatch",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #CBD5E1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }

    [data-testid="stMetricDelta"] {
        color: #94A3B8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌫️ Jamshedpur AirWatch")
st.caption("Air Quality Intelligence | Jamshedpur, Jharkhand")

st.info(
    "Data transparency: Air-quality values are model-based grid estimates "
    "from the Open-Meteo Air Quality API, not confirmed monitoring-station readings."
)

try:
    df = load_gold_data()
except (FileNotFoundError, ValueError, OSError) as error:
    st.error(f"Unable to load Gold dataset: {error}")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = df[
        (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    ]
else:
    filtered_df = df[df["date"].dt.date == selected_dates]

if filtered_df.empty:
    st.warning("No records found for the selected date range.")
    st.stop()

st.sidebar.caption(f"Showing {len(filtered_df)} of {len(df)} daily records")

# KPI metrics
st.subheader("Air Quality Overview")

avg_aqi = filtered_df["avg_us_aqi"].mean()
max_aqi = filtered_df["max_us_aqi"].max()
avg_pm25 = filtered_df["avg_pm2_5"].mean()
unhealthy_hours = filtered_df["unhealthy_hours"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average US AQI",
    f"{avg_aqi:.1f}",
    help="Mean of daily average US AQI values.",
)

col2.metric(
    "Maximum US AQI",
    f"{max_aqi:.0f}",
    help="Highest daily maximum US AQI in the selected period.",
)

col3.metric(
    "Average PM2.5",
    f"{avg_pm25:.1f}",
    help="Average daily PM2.5 concentration in source-reported units.",
)

col4.metric(
    "Unhealthy hours",
    f"{unhealthy_hours:.0f}",
    help="Sum of hourly observations with US AQI above 150.",
)

st.divider()

# AQI trend
st.subheader("AQI Trends")
st.plotly_chart(
    aqi_trend_chart(filtered_df),
    width="stretch",
)

# Pollutants and category distribution
left, right = st.columns(2)

with left:
    st.plotly_chart(
        pollutant_chart(filtered_df),
        width="stretch",
    )

with right:
    st.plotly_chart(
        daily_aqi_category_chart(filtered_df),
        width="stretch",
    )

# Daily data table
st.divider()
st.subheader("Daily Air Quality Records")

display_columns = [
    "date",
    "avg_us_aqi",
    "min_us_aqi",
    "max_us_aqi",
    "avg_pm2_5",
    "avg_pm10",
    "unhealthy_hours",
    "daily_avg_category",
]

st.dataframe(
    filtered_df[display_columns].sort_values("date", ascending=False),
    width="stretch",
    hide_index=True,
)

# Download filtered data
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data (CSV)",
    data=csv_data,
    file_name="jamshedpur_air_quality.csv",
    mime="text/csv",
)

st.caption(
    "Source: Open-Meteo Air Quality API | "
    "Location: Jamshedpur | Timezone: Asia/Kolkata"
)
