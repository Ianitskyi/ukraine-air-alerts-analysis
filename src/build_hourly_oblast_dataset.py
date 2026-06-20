from pathlib import Path
import pandas as pd

RAW_FILE = "data/raw/official_data_en.csv"
OUTPUT_FILE = "data/processed/oblast_alert_hours.csv"

EXCLUDED_OBLASTS = [
    "Crimea",
    "Sevastopol",
    "Luhanska oblast",
]

print("Loading raw data...")

df = pd.read_csv(RAW_FILE)

df = df[~df["oblast"].isin(EXCLUDED_OBLASTS)].copy()

df["started_at"] = pd.to_datetime(df["started_at"], utc=True)
df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True)

df = df[df["finished_at"] > df["started_at"]].copy()

print(f"Valid source rows: {len(df):,}")

hour_rows = []

for index, row in df.iterrows():
    oblast = row["oblast"]

    start_hour = row["started_at"].floor("h")
    end_hour = row["finished_at"].ceil("h")

    hours = pd.date_range(
        start=start_hour,
        end=end_hour,
        freq="h",
        inclusive="left"
    )

    for hour in hours:
        hour_rows.append({
            "oblast": oblast,
            "hour_start_utc": hour,
            "alert_active": 1
        })

    if index % 10000 == 0:
        print(f"Processed {index:,} rows...")

hourly = pd.DataFrame(hour_rows)

print("Removing duplicate oblast-hour rows...")

hourly = (
    hourly
    .drop_duplicates(subset=["oblast", "hour_start_utc"])
    .sort_values(["oblast", "hour_start_utc"])
)

hourly["hour_start_kyiv"] = hourly["hour_start_utc"].dt.tz_convert("Europe/Kyiv")
hourly["date"] = hourly["hour_start_kyiv"].dt.date
hourly["year"] = hourly["hour_start_kyiv"].dt.year
hourly["month"] = hourly["hour_start_kyiv"].dt.month
hourly["weekday"] = hourly["hour_start_kyiv"].dt.day_name()
hourly["hour"] = hourly["hour_start_kyiv"].dt.hour

Path("data/processed").mkdir(parents=True, exist_ok=True)
hourly.to_csv(OUTPUT_FILE, index=False)

print(f"Final oblast-hour rows: {len(hourly):,}")
print(f"Saved to: {OUTPUT_FILE}")