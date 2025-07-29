"""Streamlit example for Altex library."""

import pandas as pd
import streamlit as st

import altex

st.title("Altex Charts Demo")

st.markdown("""
This demo shows various chart types using the Altex library.
Altex provides a simple, express-like API for creating Altair charts.
""")

# Create sample data
data = pd.DataFrame(
    {
        "x": range(20),
        "y": [i**1.5 + 10 for i in range(20)],
        "category": ["A" if i % 2 == 0 else "B" for i in range(20)],
    }
)

# Chart type selector
chart_type = st.selectbox(
    "Choose a chart type:",
    ["Line Chart", "Bar Chart", "Scatter Chart", "Area Chart", "Sparkline"],
)

# Display selected chart
st.subheader(f"{chart_type} Example")

if chart_type == "Line Chart":
    altex.line_chart(
        data=data, x="x", y="y", color="category", title="Line Chart Example"
    )

elif chart_type == "Bar Chart":
    altex.bar_chart(
        data=data, x="x", y="y", color="category", title="Bar Chart Example"
    )

elif chart_type == "Scatter Chart":
    altex.scatter_chart(
        data=data, x="x", y="y", color="category", title="Scatter Chart Example"
    )

elif chart_type == "Area Chart":
    altex.area_chart(
        data=data, x="x", y="y", color="category", title="Area Chart Example"
    )

elif chart_type == "Sparkline":
    altex.sparkline_chart(
        data=data, x="x", y="y", title="Sparkline Example", height=100
    )

# Sample data examples
st.header("Sample Data Examples")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Stock Data")
    stocks = altex.get_stocks_data()
    st.write(f"Shape: {stocks.shape}")
    altex.line_chart(
        data=stocks.head(100),
        x="date",
        y="price",
        color="symbol",
        title="Stock Prices Over Time",
    )

with col2:
    st.subheader("Weather Data")
    weather = altex.get_weather_data()
    st.write(f"Shape: {weather.shape}")
    altex.scatter_chart(
        data=weather.head(100),
        x="wind",
        y="temp_max",
        title="Wind vs Temperature",
        opacity=0.6,
    )

# Sparklines section
st.header("Mini Sparklines")
stocks = altex.get_stocks_data()

col1, col2, col3 = st.columns(3)

with col1:
    goog_data = stocks.query("symbol == 'GOOG'")
    st.metric("GOOG", f"${goog_data['price'].mean():.2f}")
    altex.sparkline_chart(
        data=goog_data, x="date", y="price", height=60, autoscale_y=True
    )

with col2:
    msft_data = stocks.query("symbol == 'MSFT'")
    st.metric("MSFT", f"${msft_data['price'].mean():.2f}")
    altex.sparkline_chart(
        data=msft_data, x="date", y="price", height=60, autoscale_y=True
    )

with col3:
    aapl_data = stocks.query("symbol == 'AAPL'")
    st.metric("AAPL", f"${aapl_data['price'].mean():.2f}")
    altex.sparkline_chart(
        data=aapl_data, x="date", y="price", height=60, autoscale_y=True
    )
