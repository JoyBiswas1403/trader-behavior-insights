from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .data_loader import align_with_sentiment, daily_trader_agg, load_fear_greed, load_trades


def build_daily_join(trades_path: str, fear_greed_path: str) -> pd.DataFrame:
    trades = load_trades(trades_path)
    fng = load_fear_greed(fear_greed_path)
    daily = daily_trader_agg(trades)
    joined = align_with_sentiment(daily, fng)
    
    # Feature Engineering: Encode sentiment
    sentiment_map = {"extreme fear": 0, "fear": 1, "neutral": 2, "greed": 3, "extreme greed": 4}
    joined["sentiment_score"] = joined["classification"].map(sentiment_map)
    
    return joined


def analyze_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Compute correlation matrix for numerical columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df[numeric_cols].corr()


def cluster_traders(df: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    """Cluster traders based on their daily performance metrics."""
    # Aggregate by account to get overall trader profile
    trader_profile = df.groupby("account").agg({
        "total_pnl": "sum",
        "volume_usd": "sum",
        "trades": "sum",
        "winning_trades": "sum",
        "losing_trades": "sum"
    }).fillna(0)
    
    trader_profile["win_rate"] = trader_profile["winning_trades"] / trader_profile["trades"]
    
    features = ["total_pnl", "volume_usd", "win_rate"]
    X = trader_profile[features]
    
    # Handle infinite values if any
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    trader_profile["cluster"] = kmeans.fit_predict(X_scaled)
    
    return trader_profile


def predict_pnl(df: pd.DataFrame) -> dict:
    """Train a model to predict daily PnL based on sentiment and volume."""
    # Prepare data
    model_df = df.dropna(subset=["sentiment_score", "volume_usd", "total_pnl"]).copy()
    
    if len(model_df) < 100:
        return {"error": "Not enough data for modeling"}
        
    X = model_df[["sentiment_score", "volume_usd", "trades"]]
    y = model_df["total_pnl"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {
        "model": model,
        "mse": mse,
        "r2": r2,
        "feature_importance": dict(zip(X.columns, model.feature_importances_))
    }


if __name__ == "__main__":
    # Example usage
    df = build_daily_join(
        trades_path="data/raw/hyperliquid_trades.csv",
        fear_greed_path="data/raw/fear_greed.csv",
    )
    print("Data Loaded. Shape:", df.shape)
    
    corrs = analyze_correlations(df)
    print("\nCorrelations:\n", corrs["total_pnl"].sort_values(ascending=False))
    
    clusters = cluster_traders(df)
    print("\nTrader Clusters:\n", clusters["cluster"].value_counts())
    
    model_res = predict_pnl(df)
    if "error" not in model_res:
        print("\nModel R2 Score:", model_res["r2"])


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Calculate Sharpe Ratio (Risk-Adjusted Return)."""
    if returns.std() == 0:
        return 0.0
    return (returns.mean() - risk_free_rate) / returns.std()


def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0.0) -> float:
    """Calculate Sortino Ratio (Downside Risk-Adjusted Return)."""
    downside_returns = returns[returns < target_return]
    downside_std = downside_returns.std()
    if downside_std == 0:
        return 0.0
    return (returns.mean() - target_return) / downside_std


def calculate_max_drawdown(cumulative_returns: pd.Series) -> float:
    """Calculate Maximum Drawdown."""
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    return drawdown.min()


def predict_win_probability(df: pd.DataFrame) -> dict:
    """Train a classifier to predict the probability of the NEXT trade being a win."""
    # We need trade-level data for this, but we are working with daily aggregates in this function context.
    # Ideally, this should run on the raw trades df. 
    # For now, let's create a proxy using daily data: "Will tomorrow be a winning day?"
    
    model_df = df.sort_values(["account", "date"]).copy()
    
    # Target: Next day PnL > 0
    model_df["next_day_win"] = (model_df.groupby("account")["total_pnl"].shift(-1) > 0).astype(int)
    
    # Features: Lagged sentiment, current leverage, volume
    model_df["prev_sentiment"] = model_df.groupby("account")["sentiment_score"].shift(1)
    
    features = ["sentiment_score", "prev_sentiment", "volume_usd"]
    
    if "avg_leverage" in df.columns:
        model_df["prev_leverage"] = model_df.groupby("account")["avg_leverage"].shift(1)
        features.extend(["avg_leverage", "prev_leverage"])
    
    model_df = model_df.dropna()
    
    if len(model_df) < 50:
        return {"error": "Not enough historical data for win probability model"}
        
    X = model_df[features]
    y = model_df["next_day_win"]
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, roc_auc_score
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    
    return {
        "model": clf,
        "accuracy": accuracy_score(y_test, y_pred),
        "auc": roc_auc_score(y_test, y_prob),
        "feature_importance": dict(zip(X.columns, clf.feature_importances_))
    }


