"""
🎨 Altex Demo App

A comprehensive demonstration of the Altex library features.
Run with: streamlit run streamlit_app.py
"""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import altex

# Page config
st.set_page_config(
    page_title="Altex Demo",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Header
st.title("🎨 Altex Demo App")
st.markdown("""
**Altex** is a simple wrapper on top of Altair to make charts with an 
express API. Perfect for quick data visualization in Streamlit!

[![GitHub](https://img.shields.io/badge/GitHub-altex-blue?logo=github)](https://github.com/arnaudmiribel/altex)
[![PyPI](https://img.shields.io/badge/PyPI-altex-blue?logo=pypi)](https://pypi.org/project/altex/)
""")

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox(
    "Choose a section:",
    [
        "📊 Basic Charts",
        "✨ Sparklines",
        "📈 Sample Data",
        "🎛️ Interactive Demo",
        "📝 Code Examples",
    ],
)

if page == "📊 Basic Charts":
    st.header("📊 Basic Chart Types")

    # Create sample data
    np.random.seed(42)
    data = pd.DataFrame(
        {
            "x": range(20),
            "y": np.random.randn(20).cumsum() + 100,
            "category": ["A" if i % 2 == 0 else "B" for i in range(20)],
            "size": np.random.randint(10, 100, 20),
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Line Chart")
        altex.line_chart(
            data=data,
            x="x",
            y="y",
            color="category",
            title="Line Chart with Categories",
        )

        st.subheader("Bar Chart")
        altex.bar_chart(
            data=data.head(10),
            x="x",
            y="y",
            color="category",
            title="Bar Chart Example",
        )

    with col2:
        st.subheader("Scatter Plot")
        altex.scatter_chart(
            data=data,
            x="x",
            y="y",
            color="category",
            opacity=0.7,
            title="Scatter Plot with Opacity",
        )

        st.subheader("Area Chart")
        altex.area_chart(
            data=data, x="x", y="y", color="category", title="Area Chart Example"
        )

    # Histogram
    st.subheader("Histogram")
    hist_data = pd.DataFrame({"values": np.random.normal(100, 15, 1000)})
    altex.hist_chart(data=hist_data, x="values", title="Distribution of Random Values")

elif page == "✨ Sparklines":
    st.header("✨ Sparklines & Mini Charts")
    st.markdown("Perfect for dashboards and compact visualizations!")

    # Generate sample time series data
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    metrics_data = {
        "Revenue": np.random.normal(1000, 200, 50).cumsum(),
        "Users": np.random.normal(500, 100, 50).cumsum(),
        "Orders": np.random.normal(100, 20, 50).cumsum(),
    }

    # Metrics with sparklines
    col1, col2, col3 = st.columns(3)

    for i, (metric, values) in enumerate(metrics_data.items()):
        data = pd.DataFrame({"date": dates, "value": values})
        current_value = values[-1]

        with [col1, col2, col3][i]:
            if metric == "Revenue":
                st.metric(
                    metric,
                    f"${current_value:,.0f}",
                    f"{np.random.uniform(-5, 15):.1f}%",
                )
            else:
                st.metric(
                    metric,
                    f"{current_value:,.0f}",
                    f"{np.random.uniform(-10, 20):.1f}%",
                )

            altex.sparkline_chart(
                data=data, x="date", y="value", height=80, autoscale_y=True
            )

    # Sparkline variations
    st.subheader("Sparkline Variations")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Sparkbar Chart**")
        bar_data = pd.DataFrame({"x": range(15), "y": np.random.randint(10, 100, 15)})
        altex.sparkbar_chart(
            data=bar_data, x="x", y="y", height=100, title="Daily Activity"
        )

    with col2:
        st.write("**Sparkarea Chart**")
        area_data = pd.DataFrame(
            {"x": range(20), "y": np.random.randn(20).cumsum() + 50}
        )
        altex.sparkarea_chart(
            data=area_data, x="x", y="y", height=100, title="Growth Trend"
        )

elif page == "📈 Sample Data":
    st.header("📈 Built-in Sample Datasets")
    st.markdown("Altex includes several sample datasets for quick experimentation.")

    dataset = st.selectbox(
        "Choose a dataset:", ["Stocks", "Weather", "Barley", "Random Data"]
    )

    if dataset == "Stocks":
        st.subheader("📈 Stock Price Data")
        stocks = altex.get_stocks_data()
        st.write(f"**Shape:** {stocks.shape}")
        st.write("**Columns:**", list(stocks.columns))

        col1, col2 = st.columns([2, 1])
        with col1:
            altex.line_chart(
                data=stocks,
                x="date",
                y="price",
                color="symbol",
                title="Stock Prices Over Time",
            )
        with col2:
            st.dataframe(stocks.head(10))

    elif dataset == "Weather":
        st.subheader("🌤️ Seattle Weather Data")
        weather = altex.get_weather_data()
        st.write(f"**Shape:** {weather.shape}")
        st.write("**Columns:**", list(weather.columns))

        col1, col2 = st.columns([2, 1])
        with col1:
            altex.scatter_chart(
                data=weather.head(200),
                x="wind",
                y="temp_max",
                color="weather",
                title="Wind vs Temperature by Weather Type",
                opacity=0.6,
            )
        with col2:
            st.dataframe(weather.head(10))

    elif dataset == "Barley":
        st.subheader("🌾 Barley Yield Data")
        barley = altex.get_barley_data()
        st.write(f"**Shape:** {barley.shape}")
        st.write("**Columns:**", list(barley.columns))

        col1, col2 = st.columns([2, 1])
        with col1:
            altex.bar_chart(
                data=barley,
                x=alt.X("variety", title="Barley Variety"),
                y="sum(yield)",
                color="site",
                title="Barley Yield by Variety and Site",
            )
        with col2:
            st.dataframe(barley.head(10))

    else:  # Random Data
        st.subheader("🎲 Random Generated Data")
        random_data = altex.get_random_data()
        st.write(f"**Shape:** {random_data.shape}")
        st.write("**Columns:**", list(random_data.columns))

        col1, col2 = st.columns([2, 1])
        with col1:
            # Melt data for better visualization
            melted = pd.melt(
                random_data,
                id_vars="index",
                value_vars=["a", "b", "c"],
                var_name="series",
            )
            altex.line_chart(
                data=melted,
                x="index",
                y="value",
                color="series",
                title="Random Time Series",
            )
        with col2:
            st.dataframe(random_data.head(10))

elif page == "🎛️ Interactive Demo":
    st.header("🎛️ Interactive Chart Builder")
    st.markdown("Build your own chart with custom parameters!")

    # Data selection
    data_source = st.selectbox(
        "Choose data source:", ["Custom", "Stocks", "Weather", "Random"]
    )

    if data_source == "Custom":
        st.info("Upload your own CSV file or use the sample data below.")
        # Simple sample data
        data = pd.DataFrame(
            {
                "x": range(10),
                "y": np.random.randint(1, 100, 10),
                "category": np.random.choice(["A", "B", "C"], 10),
            }
        )
    elif data_source == "Stocks":
        data = altex.get_stocks_data().head(100)
    elif data_source == "Weather":
        data = altex.get_weather_data().head(100)
    else:
        data = altex.get_random_data()

    st.write("**Data Preview:**")
    st.dataframe(data.head())

    # Chart configuration
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Chart Settings")

        chart_type = st.selectbox(
            "Chart Type:",
            ["line_chart", "bar_chart", "scatter_chart", "area_chart", "hist_chart"],
        )

        x_col = st.selectbox("X Column:", data.columns)
        y_col = st.selectbox("Y Column:", data.columns)

        color_col = st.selectbox(
            "Color Column (optional):", [None] + list(data.columns)
        )

        chart_title = st.text_input("Chart Title:", "My Custom Chart")

        # Advanced options
        with st.expander("Advanced Options"):
            width = st.number_input("Width", min_value=100, max_value=800, value=400)
            height = st.number_input("Height", min_value=100, max_value=600, value=300)
            opacity = st.slider("Opacity", 0.1, 1.0, 1.0, 0.1)

    with col2:
        st.subheader("Your Chart")

        # Build chart parameters
        chart_params = {
            "data": data,
            "x": x_col,
            "y": y_col,
            "title": chart_title,
            "width": width,
            "height": height,
        }

        if color_col:
            chart_params["color"] = color_col

        if opacity < 1.0:
            chart_params["opacity"] = opacity

        # Create chart
        chart_func = getattr(altex, chart_type)
        chart_func(**chart_params)

else:  # Code Examples
    st.header("📝 Code Examples")
    st.markdown("Copy-paste ready examples for your projects!")

    example_type = st.selectbox(
        "Choose example:", ["Basic Usage", "Streamlit Integration", "Advanced Features"]
    )

    if example_type == "Basic Usage":
        st.subheader("🐍 Basic Python Usage")
        st.code(
            """
import altex
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'x': range(10),
    'y': [i**2 for i in range(10)],
    'category': ['A' if i % 2 == 0 else 'B' for i in range(10)]
})

# Create and display charts in Streamlit
altex.line_chart(data=data, x='x', y='y', title='Line Chart')
altex.bar_chart(data=data, x='x', y='y', color='category')
altex.scatter_chart(data=data, x='x', y='y', opacity=0.7)

# Use sample data
stocks = altex.get_stocks_data()
altex.line_chart(
    data=stocks, x='date', y='price', color='symbol'
)
        """,
            language="python",
        )

    elif example_type == "Streamlit Integration":
        st.subheader("🎯 Streamlit Integration")
        st.code(
            """
import streamlit as st
import altex

st.title("My Dashboard")

# Charts automatically display in Streamlit
altex.line_chart(
    data=altex.get_stocks_data(),
    x='date',
    y='price', 
    color='symbol',
    title='Stock Prices'
)

# Sparklines with metrics
col1, col2, col3 = st.columns(3)
stocks = altex.get_stocks_data()

with col1:
    goog_data = stocks.query("symbol == 'GOOG'")
    st.metric("GOOG", f"${goog_data['price'].mean():.2f}")
    altex.sparkline_chart(
        data=goog_data, x='date', y='price', height=60
    )
        """,
            language="python",
        )

    else:  # Advanced Features
        st.subheader("🚀 Advanced Features")
        st.code(
            """
import altex
import altair as alt

# Advanced customization with Altair objects
altex.scatter_chart(
    data=altex.get_weather_data(),
    x=alt.X('wind:Q', title='Wind Speed (mph)'),
    y=alt.Y('temp_max:Q', title='Max Temperature (°F)'),
    color=alt.Color('weather:N', legend=alt.Legend(title="Weather")),
    opacity=0.6,
    title='Seattle Weather: Wind vs Temperature'
)

# Rolling averages
altex.line_chart(
    data=altex.get_stocks_data().query("symbol == 'GOOG'"),
    x='date',
    y='price',
    rolling=7,  # 7-day rolling average
    title='GOOG Stock Price (7-day average)'
)

# Spark charts for dashboards
altex.sparkarea_chart(
    data=data,
    x='date',
    y='value',
    color=alt.Color('category', legend=None),
    height=100,
    opacity=alt.value(0.7)
)
        """,
            language="python",
        )

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666;'>
    Made with ❤️ using <strong>Altex</strong> and <strong>Streamlit</strong><br>
    <a href="https://github.com/arnaudmiribel/altex">GitHub</a> • 
    <a href="https://pypi.org/project/altex/">PyPI</a> • 
    <a href="https://altair-viz.github.io/">Altair</a>
</div>
""",
    unsafe_allow_html=True,
)
