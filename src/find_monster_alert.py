import pandas as pd

df = pd.read_csv("data/processed/alerts_oblast_merged.csv")

monster = df[df["alert_hours"] > 100]

print(monster)

print("\nCount:")
print(len(monster))