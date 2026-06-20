import pandas as pd

df = pd.read_csv("data/processed/alerts_oblast_merged.csv")

monthly = (
    df.groupby(["year", "month"])
    .agg(
        total_alert_hours=("alert_hours", "sum"),
        episodes=("oblast", "count"),
        max_alert_hours=("alert_hours", "max"),
    )
    .reset_index()
    .sort_values("total_alert_hours", ascending=False)
)

print("\nTop months by total alert hours:")
print(monthly.head(10))

top = monthly.iloc[0]
year = int(top["year"])
month = int(top["month"])

print(f"\nInspecting spike month: {year}-{month:02d}")

spike = df[(df["year"] == year) & (df["month"] == month)].copy()

by_region = (
    spike.groupby("oblast")
    .agg(
        total_alert_hours=("alert_hours", "sum"),
        episodes=("oblast", "count"),
        longest_alert_hours=("alert_hours", "max"),
    )
    .sort_values("total_alert_hours", ascending=False)
)

print("\nSpike month by region:")
print(by_region)

longest = spike.sort_values("alert_hours", ascending=False).head(20)

print("\nLongest alert episodes in spike month:")
print(longest[["oblast", "started_at_kyiv", "finished_at_kyiv", "duration_minutes", "alert_hours"]])