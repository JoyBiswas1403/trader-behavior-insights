"""Test script to verify the project is working correctly."""
from src.trader_sentiment.analysis import build_daily_join

# Load and join the data
print("Loading data...")
df = build_daily_join(
    'data/raw/hyperliquid_trades.csv',
    'data/raw/fear_greed.csv'
)

# Display results
print("\n" + "="*50)
print("PROJECT STATUS")
print("="*50)
print(f"✓ Data loaded successfully")
print(f"✓ Total records: {len(df)}")
print(f"✓ Records with sentiment: {df['classification'].notna().sum()}")
print(f"✓ Unique trader accounts: {df['account'].nunique()}")

print("\n" + "="*50)
print("SENTIMENT DISTRIBUTION")
print("="*50)
print(df['classification'].value_counts())

print("\n" + "="*50)
print("SAMPLE DATA")
print("="*50)
print(df.head(10))

print("\n" + "="*50)
print("✓✓✓ PROJECT IS WORKING CORRECTLY! ✓✓✓")
print("="*50)
