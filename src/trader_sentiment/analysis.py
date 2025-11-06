from __future__ import annotations

import pandas as pd

from .data_loader import load_trades, load_fear_greed, daily_trader_agg, align_with_sentiment


def build_daily_join(trades_path: str, fear_greed_path: str) -> pd.DataFrame:
    trades = load_trades(trades_path)
    fng = load_fear_greed(fear_greed_path)
    daily = daily_trader_agg(trades)
    joined = align_with_sentiment(daily, fng)
    return joined


if __name__ == "__main__":
    # Example usage (adjust filenames in data/raw as needed):
    df = build_daily_join(
        trades_path="data/raw/hyperliquid_trades.csv",
        fear_greed_path="data/raw/fear_greed.csv",
    )
    print(df.head())
