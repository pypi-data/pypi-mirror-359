# Altex

A simple wrapper on top of Altair to make charts in Streamlit with an express API. 

If you're lazy and/or familiar with Altair, this is probably a good fit! Inspired by tvst/plost and plotly-express.

## Installation

```bash
pip install altex
```

Or with uv (recommended):
```bash
uv add altex
```

## Quick Start

```python
import streamlit as st
import altex
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'x': range(10),
    'y': [i**2 for i in range(10)]
})

# Create and display charts in Streamlit
altex.line_chart(data=data, x='x', y='y', title='My Chart')
altex.bar_chart(data=data, x='x', y='y', color='x')
altex.scatter_chart(data=data, x='x', y='y', opacity=0.7)
```

## 🎨 Demo App

Try the interactive demo:

```bash
# Clone this repository
git clone https://github.com/arnaudmiribel/altex.git
cd altex
uv sync
uv run streamlit run streamlit_app.py
```

The demo showcases:
- 📊 Beautiful chart examples
- ✨ Sparklines for dashboards  
- 🚀 Quick start guide
- 📝 Simple API examples

## Chart Types

- `line_chart()` - Line charts
- `bar_chart()` - Bar charts  
- `area_chart()` - Area charts
- `scatter_chart()` - Scatter plots
- `hist_chart()` - Histograms
- `sparkline_chart()` - Sparkline charts
- `sparkbar_chart()` - Spark bar charts
- `sparkarea_chart()` - Spark area charts

## Features

- Simple, express-like API
- Built on top of Altair
- Automatic Streamlit integration when available
- Sample data utilities
- Support for rolling averages, custom styling, and more

## License

Apache-2.0 