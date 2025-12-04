import pandas as pd
import pytest

from src.trader_sentiment.analysis import analyze_correlations, cluster_traders


@pytest.fixture
def sample_df():
    data = {
        "account": ["A", "A", "B", "B", "C"],
        "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-02", "2023-01-01"]).date,
        "total_pnl": [100, -50, 200, 300, -100],
        "volume_usd": [1000, 1000, 2000, 2000, 500],
        "trades": [10, 10, 20, 20, 5],
        "winning_trades": [6, 4, 15, 15, 1],
        "losing_trades": [4, 6, 5, 5, 4],
        "classification": ["fear", "greed", "fear", "greed", "fear"],
        "avg_leverage": [2, 2, 5, 5, 1]
    }
    return pd.DataFrame(data)

def test_analyze_correlations(sample_df):
    corr = analyze_correlations(sample_df)
    assert "total_pnl" in corr.columns
    assert "volume_usd" in corr.columns
    assert corr.shape[0] == corr.shape[1]

def test_cluster_traders(sample_df):
    clusters = cluster_traders(sample_df, n_clusters=2)
    assert "cluster" in clusters.columns
    assert len(clusters) == 3  # 3 unique accounts
