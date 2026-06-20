import pandas as pd
from pathlib import Path

INPUT = "data/processed/oblast_alert_hours.csv"
OUTPUT = "data/processed/daily_alert_hours.csv"

print("Loading oblast-hour dataset...")

df = pd.read_csv(INPUT)

df["date"] = pd.to_datetime(df["date"])

start_date = df["date"].min()
end_date = df["date"].max()

print(f"Date range: {start_date.date()} to {end_date.date()}")

# Create a full calendar with every day, including days with zero alerts
calendar = pd.DataFrame({
    "date": pd.date_range(start=start_date, end=end_date, freq="D")
})

# Count alert-hours per day
daily_alerts = (
    df.groupby("date")
      .size()
      .reset_index(name="alert_hours")
)

# Merge with full calendar
daily = calendar.merge(daily_alerts, on="date", how="left")

# Fill days with no alerts as 0
daily["alert_hours"] = daily["alert_hours"].fillna(0).astype(int)

# Add time features
daily["year"] = daily["date"].dt.year
daily["month"] = daily["date"].dt.month
daily["weekday"] = daily["date"].dt.day_name()

Path("data/processed").mkdir(parents=True, exist_ok=True)
daily.to_csv(OUTPUT, index=False)

print(f"Rows in daily dataset: {len(daily):,}")
print(f"Saved to: {OUTPUT}")

print("\nPreview:")
print(daily.head())