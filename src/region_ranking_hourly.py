import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_csv("data/processed/oblast_alert_hours.csv")

ranking = (
    df.groupby("oblast")
    .size()
    .reset_index(name="total_alert_hours")
    .sort_values("total_alert_hours", ascending=False)
)

ranking["rank"] = range(1, len(ranking) + 1)

ranking = ranking[["rank", "oblast", "total_alert_hours"]]

print("\nREGIONS BY TOTAL OBLAST-ALERT HOURS\n")
print(ranking)

ranking.to_csv("outputs/tables/region_ranking_hourly.csv", index=False)

print("\nSaved:")
print("outputs/tables/region_ranking_hourly.csv")