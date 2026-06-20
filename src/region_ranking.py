import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_csv("data/processed/alerts_oblast_only.csv")
ranking = (
    df.groupby("oblast")
    .agg(
        alert_episodes=("oblast", "count"),
        total_alert_hours=("alert_hours", "sum"),
        avg_duration_hours=("alert_hours", "mean"),
        median_duration_hours=("alert_hours", "median"),
    )
    .sort_values("total_alert_hours", ascending=False)
)

print("\nTOP REGIONS BY TOTAL ALERT HOURS\n")
print(ranking.head(15))

ranking.to_csv(
    "outputs/tables/region_ranking.csv"
)

print("\nSaved:")
print("outputs/tables/region_ranking.csv")