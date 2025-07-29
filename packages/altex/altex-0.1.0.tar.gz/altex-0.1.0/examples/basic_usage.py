"""Basic usage examples for Altex library."""

import pandas as pd
import streamlit as st

import altex

st.title("Altex Basic Usage Examples")
st.markdown("This demonstrates the basic functionality of the Altex library.")

# Create sample data
data = pd.DataFrame(
    {
        "x": range(10),
        "y": [i**2 for i in range(10)],
        "category": ["A" if i % 2 == 0 else "B" for i in range(10)],
    }
)

st.subheader("Sample Data")
st.dataframe(data)

# Create various chart types
st.subheader("1. Line Chart")
altex.line_chart(data=data, x="x", y="y", title="Line Chart")

st.subheader("2. Bar Chart")
altex.bar_chart(data=data, x="x", y="y", title="Bar Chart")

st.subheader("3. Scatter Chart")
altex.scatter_chart(data=data, x="x", y="y", color="category", title="Scatter Chart")

# Use sample data
st.subheader("4. Using Built-in Sample Data")
stocks = altex.get_stocks_data()
st.write(f"Loaded stocks data with shape: {stocks.shape}")

altex.line_chart(
    data=stocks.head(50),
    x="date",
    y="price",
    color="symbol",
    title="Stock Prices (First 50 Records)",
)

st.success("All charts created and displayed successfully!")
st.info(
    "💡 Altex is designed specifically for Streamlit and automatically displays charts in your app."
)
