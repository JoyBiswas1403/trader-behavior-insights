# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a data analysis project examining the relationship between cryptocurrency trader performance (Hyperliquid historical executions) and Bitcoin market sentiment (Fear/Greed index). The goal is to uncover patterns and deliver insights for trading strategies by analyzing PnL, risk, leverage, and directional positioning against market sentiment.

## Development Setup

### Initial Environment Setup (Windows PowerShell)
```powershell
# Create virtual environment
py -3 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Data Acquisition
```powershell
# Download datasets from Google Drive to data/raw
python scripts\download_data.py
```

The script downloads two datasets:
- Historical trader data from Hyperliquid (trades, PnL, leverage, etc.)
- BTC Fear & Greed Index (sentiment classifications)

**Note:** After downloading, inspect `data/raw` to verify file formats (CSV/Parquet/ZIP) and update `scripts\download_data.py` output filenames if needed.

## Common Commands

### Running Analysis
```powershell
# Run the main analysis module
python -m src.trader_sentiment.analysis

# Or run directly
python src\trader_sentiment\analysis.py
```

### Working with Jupyter Notebooks
```powershell
# Start Jupyter
jupyter notebook

# Or Jupyter Lab
jupyter lab
```

Notebooks should be placed in the `notebooks/` directory for EDA and prototyping.

### Testing Python Scripts
```powershell
# Run a specific module
python -m src.trader_sentiment.data_loader

# Run scripts
python scripts\download_data.py
```

## Architecture & Code Structure

### Package Organization

**`src/trader_sentiment/`** - Main Python package containing core analysis logic:

- **`data_loader.py`** - Data ingestion and preprocessing pipeline
  - `load_fear_greed()`: Loads and normalizes BTC sentiment data (date + classification)
  - `load_trades()`: Loads Hyperliquid trade data (supports CSV/Parquet)
  - `daily_trader_agg()`: Aggregates trades by account/day, computing PnL, volume, long/short bias, leverage
  - `align_with_sentiment()`: Joins aggregated trader metrics with sentiment data by date
  - `Paths` dataclass: Manages data directory paths

- **`analysis.py`** - High-level analysis orchestration
  - `build_daily_join()`: End-to-end pipeline that loads both datasets, aggregates trades, and joins with sentiment

### Data Flow Architecture

1. **Raw Data Ingestion** (`data/raw/`)
   - Fear/Greed CSV: `date`, `classification` (fear/greed labels)
   - Hyperliquid trades: `account`, `symbol`, `time`, `size`, `side`, `closedPnL`, `leverage`, etc.

2. **Data Normalization** (in `data_loader.py`)
   - Column names standardized to lowercase
   - Datetime parsing with UTC timezone handling
   - Flexible column detection (handles variations like "time"/"timestamp", "pnl"/"closedPnL")

3. **Aggregation** (`daily_trader_agg()`)
   - Groups by `account` + `date`
   - Computes: total PnL, trade volume, trade count, long bias ratio, average leverage

4. **Sentiment Alignment** (`align_with_sentiment()`)
   - Left-joins daily trader aggregates with Fear/Greed index on date
   - Preserves all trader data, adds sentiment classification where available

5. **Analysis Output** (`data/processed/`)
   - Generated/cleaned datasets stored here
   - Excluded from git (see `.gitignore`)

### Key Design Patterns

- **Flexible data loading**: Tries CSV first, falls back to Parquet; handles column name variations
- **Dataclass for paths**: `Paths.from_repo()` provides consistent path management
- **Defensive aggregation**: Uses `min_count=1` to avoid spurious zeros when all values are NaN
- **Date-based alignment**: All temporal joins operate on date-only (not datetime) to avoid timezone issues

## Dataset Details

### Google Drive File IDs
- Historical Trader Data: `1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs`
- Fear/Greed Index: `1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf`

### Expected Schemas

**Fear/Greed Index:**
- `Date`: Date of sentiment reading
- `Classification`: Sentiment label (e.g., "Fear", "Greed", "Extreme Fear", "Extreme Greed")

**Hyperliquid Trades:**
- `account`: Trader identifier
- `symbol`: Trading pair
- `time`: Execution timestamp
- `size`: Trade size (volume)
- `side`: "buy"/"sell" or "long"/"short"
- `closedPnL`: Realized profit/loss
- `leverage`: Leverage used
- `execution price`, `start position`, `event`: Additional trade context

## Analysis Guidelines

When extending analysis, follow this pattern:

1. **Data ingestion**: Use existing loaders in `data_loader.py` for consistency
2. **Feature engineering**: Add functions to `data_loader.py` for reusable transformations (e.g., rolling windows, sentiment regime detection)
3. **Analysis logic**: Add high-level workflows to `analysis.py`
4. **Exploratory work**: Prototype in `notebooks/` before productionizing

### Suggested Analysis Areas
- PnL correlation with sentiment regimes
- Leverage usage patterns during extreme fear/greed
- Long/short bias shifts relative to sentiment
- Win rate and risk metrics by sentiment classification
- Temporal patterns (rolling windows, sentiment turning points)

## Important Notes

- **Virtual environment**: Always activate `.venv` before working
- **Data privacy**: Raw and processed data are gitignored; never commit actual datasets
- **Filename flexibility**: The download script may need adjustment based on actual file formats
- **Windows paths**: Use backslashes (`\`) or raw strings when working with file paths in PowerShell
