
import pandas as pd
import requests


def fetch_recent_trades(coin: str = "BTC") -> pd.DataFrame:
    """
    Fetch recent trades for a specific coin from Hyperliquid API.
    Endpoint: https://api.hyperliquid.xyz/info
    """
    url = "https://api.hyperliquid.xyz/info"
    payload = {
        "type": "l2Book", 
        "coin": coin
    }
    # Note: 'recentTrades' might be the better type if available, but let's check l2Book or similar first.
    # Actually, let's use the 'recentTrades' type as found in research.
    
    payload = {"type": "recentTrades", "coin": coin}
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        
        # Data structure is typically a list of dicts
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Normalize columns to match our historical schema where possible
        # Expected fields: coin, side, px, sz, time, hash
        
        df["price"] = df["px"].astype(float)
        df["size"] = df["sz"].astype(float)
        df["volume_usd"] = df["price"] * df["size"]
        df["side"] = df["side"].apply(lambda x: "Buy" if x == "B" else "Sell")
        df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
        df["date"] = df["time"].dt.date
        
        # Add dummy fields to match historical schema for compatibility
        df["account"] = "Live_Market_User" # We don't get account IDs in public trade feeds usually
        df["total_pnl"] = 0.0 # Can't know PnL from public feed
        df["avg_leverage"] = 1.0 # Unknown
        
        return df
        
    except Exception as e:
        print(f"Error fetching live data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_recent_trades()
    print(df.head())
    print(df.columns)
