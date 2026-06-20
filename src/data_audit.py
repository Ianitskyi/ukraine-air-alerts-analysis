from pathlib import Path
import pandas as pd

url = "https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/official_data_en.csv"

print("Loading dataset...")

df = pd.read_csv(url)

print("\nDATASET OVERVIEW")
print("-" * 40)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")
for c in df.columns:
    print(f" - {c}")

print("\nMissing values:")
print(df.isna().sum())

print("\nUnique oblasts:")
print(sorted(df["oblast"].dropna().unique()))

print(f"\nNumber of oblasts: {df['oblast'].nunique()}")

print("\nDate range:")

df["started_at"] = pd.to_datetime(df["started_at"])
df["finished_at"] = pd.to_datetime(df["finished_at"])

print("First alert:", df["started_at"].min())
print("Last alert :", df["finished_at"].max())

print("\nAdministrative levels:")
print(df["level"].value_counts())

print("\nSources:")
print(df["source"].value_counts())