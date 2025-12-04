# 🚀 Trader Behavior Insights

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)
[![Live Demo](https://img.shields.io/badge/Demo-Click%20Here-blueviolet)](https://trader-behavior-insights-dgmypmic4s3ccltjwmzy9m.streamlit.app/)

**A professional-grade Quantitative Intelligence Platform analyzing the relationship between Bitcoin Market Sentiment and Trader Performance.**

![Demo](assets/demo.webp)

## 🌟 Key Features

### 🧠 Quant Analysis
- **Risk-Adjusted Metrics**: Automatically calculates **Sharpe Ratio**, **Sortino Ratio**, and **Max Drawdown** for top traders.
- **Performance Profiling**: Identifies consistent winners vs. high-risk gamblers.

### 🔮 Win Probability Model (ML)
- **Predictive Engine**: Uses a **Random Forest Classifier** to predict the probability of the *next* trading day being profitable.
- **Feature Engineering**: Incorporates Sentiment Score, Volume, and Leverage patterns.
- **Explainable AI**: Visualizes feature importance to show *why* a prediction was made.

### ⚡ Live Market Data
- **Real-Time Feed**: Connects directly to the **Hyperliquid API** to fetch live trade executions.
- **Live Visualization**: Watch price action and order flow in real-time.

### 👥 Trader Clustering
- **Unsupervised Learning**: Uses **K-Means Clustering** to segment traders into behavioral archetypes (e.g., "Whales", "Scalpers", "Bag Holders").

---

## 🛠️ Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/JoyBiswas1403/trader-behavior-insights.git
cd trader-behavior-insights
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
trader-behavior-insights/
├── src/
│   └── trader_sentiment/
│       ├── analysis.py       # Core logic for ML, Clustering, and Quant Metrics
│       ├── data_loader.py    # Data ingestion and cleaning pipeline
│       └── live_data.py      # Real-time Hyperliquid API connector
├── tests/                    # Unit tests (pytest)
├── data/                     # Raw and processed datasets
├── app.py                    # Streamlit Dashboard entry point
└── requirements.txt          # Project dependencies
```

---

## 🧪 Testing

Run the test suite to verify data integrity and calculation logic:
```bash
pytest
```

---

## 📊 Methodology

1.  **Data Ingestion**: Historical trades are loaded from CSV/Parquet and aligned with daily Fear/Greed Index values.
2.  **Feature Engineering**: We compute rolling averages, daily PnL, and sentiment lags.
3.  **Modeling**:
    *   **Clustering**: Standardized features (`volume`, `pnl`, `win_rate`) -> K-Means.
    *   **Prediction**: `RandomForestClassifier` trained on 80/20 split.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a Pull Request.

---

**Author**: Joy Biswas
**License**: MIT
