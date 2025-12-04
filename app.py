
import pandas as pd
import plotly.express as px
import streamlit as st

from src.trader_sentiment.analysis import (
    analyze_correlations,
    build_daily_join,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    cluster_traders,
    predict_win_probability,
)
from src.trader_sentiment.live_data import fetch_recent_trades

st.set_page_config(page_title="Trader Behavior Insights", layout="wide")

@st.cache_data
def load_data():
    return build_daily_join(
        trades_path="data/raw/hyperliquid_trades.csv",
        fear_greed_path="data/raw/fear_greed.csv",
    )

def main():
    st.title("Trader Behavior Insights 🚀")
    st.markdown("Analyzing the relationship between **Bitcoin Market Sentiment** and **Trader Performance**.")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # Sidebar
    st.sidebar.header("Filters")
    selected_sentiment = st.sidebar.multiselect(
        "Select Sentiment Class",
        options=df["classification"].unique(),
        default=df["classification"].unique()
    )
    
    filtered_df = df[df["classification"].isin(selected_sentiment)]

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", f"{filtered_df['trades'].sum():,}")
    col2.metric("Total Volume", f"${filtered_df['volume_usd'].sum():,.0f}")
    col3.metric("Total PnL", f"${filtered_df['total_pnl'].sum():,.0f}")
    col4.metric("Avg Leverage", f"{filtered_df['avg_leverage'].mean():.2f}x" if "avg_leverage" in filtered_df.columns else "N/A")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Market Analysis", "👥 Trader Clustering", "🧠 Quant Analysis", "🔮 Win Prob Model", "⚡ Live Market"])

    with tab1:
        st.subheader("Market Sentiment vs Performance")
        
        # PnL over time colored by sentiment
        fig_pnl = px.scatter(
            filtered_df, x="date", y="total_pnl", color="classification",
            title="Daily PnL by Sentiment", hover_data=["account"],
            color_discrete_map={
                "extreme fear": "red", "fear": "orange", 
                "neutral": "gray", "greed": "lightgreen", "extreme greed": "green"
            }
        )
        st.plotly_chart(fig_pnl, use_container_width=True)
        
        # Correlation Matrix
        st.subheader("Correlation Analysis")
        corrs = analyze_correlations(filtered_df)
        fig_corr = px.imshow(corrs, text_auto=True, title="Feature Correlations")
        st.plotly_chart(fig_corr, use_container_width=True)

    with tab2:
        st.subheader("Trader Segmentation")
        if st.button("Run Clustering Analysis"):
            with st.spinner("Clustering traders..."):
                clusters = cluster_traders(df)
                
                fig_cluster = px.scatter(
                    clusters, x="volume_usd", y="total_pnl", color="cluster",
                    size="trades", hover_name=clusters.index,
                    title="Trader Clusters (Volume vs PnL)",
                    log_x=True
                )
                st.plotly_chart(fig_cluster, use_container_width=True)
                
                st.write("### Top Traders in Each Cluster")
                for i in range(3):
                    st.write(f"**Cluster {i}**")
                    st.dataframe(clusters[clusters["cluster"] == i].sort_values("total_pnl", ascending=False).head(5))

    with tab3:
        st.subheader("Advanced Quant Metrics")
        st.markdown("Risk-adjusted performance metrics for the top 5 profitable traders.")
        
        top_traders = df.groupby("account")["total_pnl"].sum().sort_values(ascending=False).head(5).index.tolist()
        
        metrics_data = []
        for account in top_traders:
            trader_df = df[df["account"] == account].sort_values("date")
            returns = trader_df["total_pnl"]
            
            sharpe = calculate_sharpe_ratio(returns)
            sortino = calculate_sortino_ratio(returns)
            max_dd = calculate_max_drawdown(returns.cumsum())
            
            metrics_data.append({
                "Account": account,
                "Total PnL": trader_df["total_pnl"].sum(),
                "Sharpe Ratio": sharpe,
                "Sortino Ratio": sortino,
                "Max Drawdown": max_dd
            })
            
        st.dataframe(pd.DataFrame(metrics_data).style.format({
            "Total PnL": "${:,.2f}",
            "Sharpe Ratio": "{:.2f}",
            "Sortino Ratio": "{:.2f}",
            "Max Drawdown": "{:.2%}"
        }))

    with tab4:
        st.subheader("Win Probability Model (Next Trade Prediction)")
        st.markdown("Predicting the probability that the **NEXT** day will be profitable based on sentiment and leverage.")
        
        if st.button("Train Win Prob Model"):
            with st.spinner("Training Random Forest Classifier..."):
                res = predict_win_probability(df)
                
                if "error" in res:
                    st.error(res["error"])
                else:
                    c1, c2 = st.columns(2)
                    c1.metric("Model Accuracy", f"{res['accuracy']:.2%}")
                    c2.metric("ROC AUC Score", f"{res['auc']:.4f}")
                    
                    st.write("### Feature Importance")
                    imp_df = pd.DataFrame(list(res["feature_importance"].items()), columns=["Feature", "Importance"])
                    fig_imp = px.bar(imp_df, x="Feature", y="Importance", title="Predictive Factors")
                    st.plotly_chart(fig_imp, use_container_width=True)

    with tab5:
        st.subheader("⚡ Live Market Data (Hyperliquid)")
        
        if st.button("Fetch Live Trades"):
            with st.spinner("Fetching recent trades from Hyperliquid..."):
                live_df = fetch_recent_trades("BTC")
                
                if not live_df.empty:
                    st.success(f"Fetched {len(live_df)} recent trades!")
                    
                    # Live Metrics
                    l1, l2, l3 = st.columns(3)
                    l1.metric("Current Price", f"${live_df['price'].iloc[0]:,.2f}")
                    l2.metric("24h Volume (Sample)", f"${live_df['volume_usd'].sum():,.0f}")
                    l3.metric("Latest Trade Side", live_df['side'].iloc[0])
                    
                    st.dataframe(live_df[["time", "side", "price", "size", "volume_usd"]])
                    
                    # Live Chart
                    fig_live = px.line(live_df, x="time", y="price", title="Live BTC Price Action")
                    st.plotly_chart(fig_live, use_container_width=True)
                else:
                    st.warning("No live data fetched. Check API connection.")

if __name__ == "__main__":
    main()

