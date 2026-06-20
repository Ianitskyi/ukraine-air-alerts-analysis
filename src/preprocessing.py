from pathlib import Path
import math
import pandas as pd

RAW_FILE = "data/raw/official_data_en.csv"
PROCESSED_FILE = "data/processed/alerts_clean.csv"

EXCLUDED_OBLASTS = [
    "Crimea",
    "Sevastopol",
    "Luhanska oblast",
]

print("Loading raw data...")

df = pd.read_csv(RAW_FILE)

print(f"Raw rows: {len(df):,}")

# Convert timestamps
df["started_at"] = pd.to_datetime(df["started_at"], utc=True)
df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)

# Remove excluded territories
df = df[~df["oblast"].isin(EXCLUDED_OBLASTS)].copy()

# Calculate duration
df["duration_minutes"] = (
    df["finished_at"] - df["started_at"]
).dt.total_seconds() / 60

# Keep only valid positive durations
df = df[df["duration_minutes"] > 0].copy()

# Methodology: any positive alert shorter than 1 hour counts as 1 hour
df["alert_hours"] = df["duration_minutes"].apply(lambda x: max(1, math.ceil(x / 60)))

# Convert to Kyiv time for analysis
df["started_at_kyiv"] = df["started_at"].dt.tz_convert("Europe/Kyiv")
df["finished_at_kyiv"] = df["finished_at"].dt.tz_convert("Europe/Kyiv")

# Time features
df["date"] = df["started_at_kyiv"].dt.date
df["year"] = df["started_at_kyiv"].dt.year
df["month"] = df["started_at_kyiv"].dt.month
df["weekday"] = df["started_at_kyiv"].dt.day_name()
df["hour"] = df["started_at_kyiv"].dt.hour

# Save cleaned data
Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_csv(PROCESSED_FILE, index=False)

print(f"Clean rows: {len(df):,}")
print(f"Saved to: {PROCESSED_FILE}")

print("\nRows by oblast:")
print(df["oblast"].value_counts().sort_index())