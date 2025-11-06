# Trader Behavior Insights: BTC Market Sentiment vs. Trader Performance

This project explores the relationship between trader performance (Hyperliquid historical executions) and Bitcoin market sentiment (Fear/Greed index). You'll ingest and align both datasets, engineer features, and analyze how sentiment correlates with PnL, risk, leverage, and directional positioning.

Links to datasets
- Historical Trader Data (Google Drive): https://drive.google.com/file/d/1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs/view?usp=sharing
- BTC Fear & Greed Index (Google Drive): https://drive.google.com/file/d/1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf/view?usp=sharing

Quickstart (Windows PowerShell)
1) Create and activate a virtual environment
   - py -3 -m venv .venv
   - .\.venv\Scripts\Activate.ps1
2) Install dependencies
   - pip install -r requirements.txt
3) Download datasets to data\raw using the provided file IDs
   - python scripts\download_data.py
4) Explore
   - Open notebooks or build analyses in src\trader_sentiment\

Project structure
- src\trader_sentiment: Python package for data loading, preprocessing, and analysis
- data\raw: Place raw datasets here (kept out of git)
- data\processed: Generated/cleaned datasets
- notebooks: EDA and prototyping
- scripts: Utility scripts (e.g., data download)

Notes on the Google Drive downloads
- This repo includes a small downloader using gdown that fetches by file ID:
  - Historical Trader Data ID: 1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs
  - Fear/Greed Index ID: 1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf
- The actual file formats (CSV/Parquet/ZIP) may vary; update scripts\download_data.py output names if needed after downloading.

Assignment framing (from prompt)
You will work with:
1) Bitcoin Market Sentiment Dataset
   - Columns: Date, Classification (Fear/Greed)
2) Historical Trader Data from Hyperliquid
   - Columns include: account, symbol, execution price, size, side, time, start position, event, closedPnL, leverage, etc.
Goal: Explore the relationship between trader performance and market sentiment, uncover patterns, and deliver insights for smarter trading strategies.

Suggested analysis outline
- Ingest and normalize schemas (parse datetimes, standardize column names)
- Aggregate trades by account/day; compute PnL, win rate, gross/net exposure, leverage usage, long/short bias
- Align with Fear/Greed by date; create sentiment features (one-hot, rolling windows, turning points)
- Model/visualize relationships (e.g., PnL vs. sentiment regime, leverage vs. sentiment)
- Report key findings and caveats

Applying
Send your resume and completed assignment (GitHub, portfolio, blog, etc.) to:
- saami@bajarangs.com, nagasai@bajarangs.com, chetan@bajarangs.com
- cc: sonika@primetrade.ai
Subject: "Junior Data Scientist – Trader Behavior Insights"
