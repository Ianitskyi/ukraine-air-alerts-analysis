from pathlib import Path
import math
import pandas as pd

INPUT = "data/processed/alerts_clean.csv"
OUTPUT = "data/processed/alerts_oblast_merged.csv"

print("Loading cleaned data...")

df = pd.read_csv(INPUT)

df["started_at_kyiv"] = pd.to_datetime(df["started_at_kyiv"], utc=True)
df["finished_at_kyiv"] = pd.to_datetime(df["finished_at_kyiv"], utc=True)

merged_rows = []

for oblast, group in df.groupby("oblast"):
    group = group.sort_values("started_at_kyiv")

    current_start = None
    current_end = None

    for _, row in group.iterrows():
        start = row["started_at_kyiv"]
        end = row["finished_at_kyiv"]

        if current_start is None:
            current_start = start
            current_end = end
        elif start <= current_end:
            # Overlapping alert: extend current episode
            current_end = max(current_end, end)
        else:
            # Save previous episode
            duration_minutes = (current_end - current_start).total_seconds() / 60
            alert_hours = max(1, math.ceil(duration_minutes / 60))

            merged_rows.append({
                "oblast": oblast,
                "started_at_kyiv": current_start,
                "finished_at_kyiv": current_end,
                "duration_minutes": duration_minutes,
                "alert_hours": alert_hours,
            })

            current_start = start
            current_end = end

    if current_start is not None:
        duration_minutes = (current_end - current_start).total_seconds() / 60
        alert_hours = max(1, math.ceil(duration_minutes / 60))

        merged_rows.append({
            "oblast": oblast,
            "started_at_kyiv": current_start,
            "finished_at_kyiv": current_end,
            "duration_minutes": duration_minutes,
            "alert_hours": alert_hours,
        })

merged = pd.DataFrame(merged_rows)

merged["date"] = merged["started_at_kyiv"].dt.date
merged["year"] = merged["started_at_kyiv"].dt.year
merged["month"] = merged["started_at_kyiv"].dt.month
merged["weekday"] = merged["started_at_kyiv"].dt.day_name()
merged["hour"] = merged["started_at_kyiv"].dt.hour

Path("data/processed").mkdir(parents=True, exist_ok=True)
merged.to_csv(OUTPUT, index=False)

print(f"Original rows: {len(df):,}")
print(f"Merged oblast episodes: {len(merged):,}")
print(f"Saved to: {OUTPUT}")