import pandas as pd
df = pd.read_csv('public/data/raw/CHAMBLFERT_NS.csv', index_col=0)
print('CSV Data (last 10 rows):')
print(df[['Open', 'High', 'Low', 'Close']].tail(10))
print()
print('Min/Max in entire CSV:')
print(f'  Min Close: Rs{df["Close"].min():.2f}')
print(f'  Max Close: Rs{df["Close"].max():.2f}')
