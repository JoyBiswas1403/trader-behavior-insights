from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class Paths:
    repo_root: str
    raw_dir: str
    processed_dir: str

    @classmethod
    def from_repo(cls, repo_root: str) -> "Paths":
        return cls(
            repo_root=repo_root,
            raw_dir=os.path.join(repo_root, "data", "raw"),
            processed_dir=os.path.join(repo_root, "data", "processed"),
        )


def load_fear_greed(path: str) -> pd.DataFrame:
    """Load BTC Fear/Greed index. Expects columns like ['Date', 'Classification'].
    Parses Date to datetime (UTC, date-only).
    """
    df = pd.read_csv(path)
    # Normalize columns
    cols = {c: c.strip().lower() for c in df.columns}
    df = df.rename(columns=cols)
    # Parse date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.tz_localize("UTC", nonexistent="shift_forward", ambiguous="NaT").dt.date
    # Ensure classification exists
    if "classification" in df.columns:
        df["classification"] = df["classification"].str.strip().str.lower()
    return df


def load_trades(path: str) -> pd.DataFrame:
    """Load Hyperliquid historical trader executions.
    Attempts CSV first; if that fails, tries Parquet.
    """
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.read_parquet(path)
    # Normalize
    df.columns = [c.strip().lower() for c in df.columns]
    # Parse time
    time_col = None
    for candidate in ("timestamp", "time", "ts"):
        if candidate in df.columns:
            time_col = candidate
            break
    if time_col:
        # Try milliseconds first (common in crypto data), then regular datetime
        try:
            df[time_col] = pd.to_datetime(df[time_col], unit="ms", utc=True)
        except (ValueError, TypeError):
            df[time_col] = pd.to_datetime(df[time_col], errors="coerce", utc=True)
        df["date"] = df[time_col].dt.date
    return df


def daily_trader_agg(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per account per day: PnL, volume, trades, long/short bias, leverage."""
    cols = set(df.columns)
    pnl_col = next((c for c in ["closed pnl", "closedpnl", "pnl", "realizedpnl"] if c in cols), None)
    size_usd_col = next((c for c in ["size usd", "size_usd", "notional"] if c in cols), None)
    size_col = next((c for c in ["size tokens", "size", "qty", "quantity"] if c in cols), None)
    side_col = next((c for c in ["side", "direction"] if c in cols), None)
    lev_col = "leverage" if "leverage" in cols else None
    fee_col = "fee" if "fee" in cols else None

    def long_bias(s: pd.Series) -> float:
        if s.empty:
            return 0.0
        longs = (s.str.lower() == "buy") | (s.str.lower() == "long")
        return float(longs.mean())

    group_keys = ["account", "date"] if {"account", "date"}.issubset(cols) else [c for c in ["account", "date"] if c in cols]
    g = df.groupby(group_keys, dropna=False)
    out = pd.DataFrame()
    out["trades"] = g.size()
    if pnl_col:
        out["total_pnl"] = g[pnl_col].sum(min_count=1)
        out["avg_pnl_per_trade"] = g[pnl_col].mean()
        out["winning_trades"] = g[pnl_col].apply(lambda x: (x > 0).sum())
        out["losing_trades"] = g[pnl_col].apply(lambda x: (x < 0).sum())
    if size_usd_col:
        out["volume_usd"] = g[size_usd_col].apply(lambda x: x.abs().sum())
    elif size_col:
        out["volume"] = g[size_col].apply(lambda x: x.abs().sum())
    if side_col:
        out["long_bias"] = g[side_col].apply(long_bias)
    if lev_col:
        out["avg_leverage"] = g[lev_col].mean()
    if fee_col:
        out["total_fees"] = g[fee_col].sum(min_count=1)
    return out.reset_index()


def align_with_sentiment(agg: pd.DataFrame, fng: pd.DataFrame) -> pd.DataFrame:
    """Left-join daily aggregates with Fear/Greed on date."""
    if "date" not in agg.columns:
        raise ValueError("Aggregates must contain a 'date' column")
    if "date" not in fng.columns:
        raise ValueError("Fear/Greed must contain a 'date' column")
    return agg.merge(fng[["date", "classification"]], on="date", how="left")
