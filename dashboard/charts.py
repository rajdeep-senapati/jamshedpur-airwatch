"""Reusable Plotly visualizations for Jamshedpur AirWatch."""

import plotly.express as px
import plotly.graph_objects as go

AQI_COLORS = {
    "Good": "#16A34A",
    "Moderate": "#EAB308",
    "Unhealthy for Sensitive Groups": "#F97316",
    "Unhealthy": "#DC2626",
    "Very Unhealthy": "#9333EA",
    "Hazardous": "#7F1D1D",
}


def aqi_trend_chart(df):
    """Show daily average and maximum US AQI."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["avg_us_aqi"],
            name="Average AQI",
            mode="lines+markers",
            line=dict(color="#2563EB", width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["max_us_aqi"],
            name="Maximum AQI",
            mode="lines+markers",
            line=dict(color="#DC2626", width=2, dash="dot"),
        )
    )

    fig.update_layout(
        title="Daily Air Quality Index",
        xaxis_title="Date",
        yaxis_title="US AQI",
        hovermode="x unified",
        template="plotly_white",
        legend_title="Metric",
    )

    return fig


def pollutant_chart(df):
    """Compare average daily pollutant concentrations."""

    pollutants = {
        "PM2.5": "avg_pm2_5",
        "PM10": "avg_pm10",
        "NO2": "avg_nitrogen_dioxide",
        "Ozone": "avg_ozone",
        "SO2": "avg_sulphur_dioxide",
        "CO": "avg_carbon_monoxide",
    }

    values = [
        {
            "Pollutant": name,
            "Concentration": df[column].mean(),
        }
        for name, column in pollutants.items()
    ]

    values_df = __import__("pandas").DataFrame(values)
    values_df = values_df.sort_values("Concentration")

    fig = px.bar(
        values_df,
        x="Concentration",
        y="Pollutant",
        orientation="h",
        text_auto=".1f",
        title="Average Pollutant Concentrations",
        color="Pollutant",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    fig.update_layout(
        template="plotly_dark",
        showlegend=False,
        xaxis_title="Average concentration (µg/m³)",
        yaxis_title="",
        height=420,
        margin=dict(l=20, r=20, t=60, b=40),
    )

    return fig


def daily_aqi_category_chart(df):
    """Show the daily average AQI category distribution."""
    counts = df["daily_avg_category"].value_counts().reset_index()

    counts.columns = ["Category", "Days"]

    fig = px.bar(
        counts,
        x="Category",
        y="Days",
        color="Category",
        color_discrete_map=AQI_COLORS,
        title="Days by AQI Category",
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False,
    )

    return fig
