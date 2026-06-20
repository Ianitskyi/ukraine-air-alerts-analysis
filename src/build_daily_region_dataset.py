import pandas as pd
from pathlib import Path

INPUT = "data/processed/oblast_alert_hours.csv"
OUTPUT = "data/processed/daily_region_alert_hours.csv"

print("Loading oblast-hour dataset...")

df = pd.read_csv(INPUT)

df["date"] = pd.to_datetime(df["date"])

# Count alert-hours per date and region
daily_region = (
    df.groupby(["date", "oblast"])
      .size()
      .reset_index(name="alert_hours")
)

# Add full calendar for every date-region pair, including zero-alert days
all_dates = pd.date_range(
    start=df["date"].min(),
    end=df["date"].max(),
    freq="D"
)

all_oblasts = sorted(df["oblast"].unique())

calendar = pd.MultiIndex.from_product(
    [all_dates, all_oblasts],
    names=["date", "oblast"]
).to_frame(index=False)

daily_region = calendar.merge(
    daily_region,
    on=["date", "oblast"],
    how="left"
)

daily_region["alert_hours"] = daily_region["alert_hours"].fillna(0).astype(int)

daily_region["year"] = daily_region["date"].dt.year
daily_region["month"] = daily_region["date"].dt.month
daily_region["weekday"] = daily_region["date"].dt.day_name()

Path("data/processed").mkdir(parents=True, exist_ok=True)
daily_region.to_csv(OUTPUT, index=False)

print(f"Rows: {len(daily_region):,}")
print(f"Regions: {daily_region['oblast'].nunique()}")
print(f"Date range: {daily_region['date'].min().date()} to {daily_region['date'].max().date()}")
print(f"Saved to: {OUTPUT}")

print("\nPreview:")
print(daily_region.head(20))