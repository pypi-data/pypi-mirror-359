# 🧠 DataWhisperer

**Talk to your DataFrame. Literally.**

`DataWhisperer` is a professional-grade Python library that enables interaction with `pandas` DataFrames using natural language. Powered by LLMs like **OpenAI** and **Google Gemini**, it transforms analytical questions into executable Python code. Whether you need summaries, transformations, or visualizations, DataWhisperer delivers accurate results and adapts dynamically to your data structure.

> ✨ No more `.groupby()`, `.pivot()` or plotting boilerplate. Just whisper to your data.

---

## 🚀 Key Features

* 🔗 Natural Language to Python code conversion for DataFrames
* 📊 Auto-generated visualizations with Plotly
* 🛠️ Automatic error detection & self-repair with multi-step retry logic
* 🧠 Supports **OpenAI**, **Gemini**, and is extensible to Claude, LLaMA, Mistral (coming soon)
* 🔁 Smart retry strategy for broken code (`max_retries`)
* 🧼 Schema-driven prompt system (auto-describes your columns)
* 🧪 Modular and testable architecture
* 🧩 Plugin-ready and LLM-client agnostic (future-proof)

---

## 📦 Installation

Install from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ datawhisperer
```

Or, for local development:

```bash
git clone https://github.com/JosueARz/DataWhisperer.git
cd DataWhisperer
pip install -e .
```

Requirements: Python 3.8+

---

## ⚡ Quick Start

```python
from datawhisperer import DataFrameChatbot
import pandas as pd

# Load your dataset
data = pd.read_csv("sales_data.csv")

# Describe the columns
schema = {
    "region": "Sales region (e.g., North, South, East, West)",
    "sales": "Amount of revenue generated",
    "date": "Date of the sale"
}

# Create the chatbot
bot = DataFrameChatbot(
    api_key="your-api-key",
    model="gpt-4",  # or "gemini-1.5-flash"
    dataframe=data,
    schema=schema,
    max_retries=3  # Number of auto-repair attempts if execution fails
)

# Ask a question
response = bot.ask_and_run("Show a bar chart of total sales per region")

# Display result
print(response.text)
response.table  # Or: response.chart
```

---

## 🧠 What kind of questions can I ask?

* "Which region had the highest revenue in Q2?"
* "Show average sales by month."
* "Plot a heatmap of transactions by region and month."
* "How many sales were made after July 15th?"
* "Which regions had declining revenue trends over time?"

> DataWhisperer will generate optimized and runnable Python code — and automatically fix it if it fails.

---

## ✅ Example Output

### 🔍 Input (user question):

> "What are the top 3 regions by total sales?"

### 🧪 Output (Python code):

```python
import pandas as pd
import plotly.express as px

# Group and sort data
top_regions = df.groupby("region")["sales"].sum().sort_values(ascending=False).head(3).reset_index()
print("Top 3 regions by total sales:")

# Display table
top_regions
```

### 📋 Output (text + table):

```
Top 3 regions by total sales:
```

| region | sales     |
| ------ | --------- |
| North  | 102,400.0 |
| East   | 98,900.0  |
| South  | 87,120.0  |

---

## 🧪 Testing the Library

```bash
pytest
pytest --cov=datawhisperer --cov-report=term-missing
```

### Coverage Includes:

* Code generation & formatting (`PromptFactory`)
* Code execution & error repair (`executor.py`)
* Retry logic & self-healing (`fixer.py`)
* Chat interface orchestration (`DataFrameChatbot`)

> Note: Tests use fake LLM clients to avoid real API calls.

---

## 📌 Version

**Current release:** `v0.1.4`

See the [CHANGELOG.md](./CHANGELOG.md) for updates.

Upcoming versions will include:

* SQL + Python-SQL modes
* Multiple LLM client support
* DuckDB, SQLite, Postgres connectors
* CLI + Streamlit interface
* Plugin hooks

---

## 📖 Documentation

Full documentation will be hosted via **MkDocs** in future release `v1.0.0`.

* Quickstart & API Reference
* Examples & Recipes
* Plugin Development Guide

---

## 📄 License

Apache License 2.0 — use it freely, contribute professionally.
© 2024 JosueARz

---

## 🤝 Contributing

Pull requests are welcome. Please ensure your changes are:

* Type hinted and PEP8-compliant
* Tested with pytest
* Explained clearly in PR descriptions

---

## 🧙 Why "Whisperer"?

Because it doesn’t just chat — it understands your data.
