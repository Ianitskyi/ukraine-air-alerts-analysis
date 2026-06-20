import pandas as pd

INPUT = "data/processed/daily_region_alert_hours.csv"
OUTPUT = "outputs/tables/regional_risk_index.csv"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", "{:.2f}".format)

df = pd.read_csv(INPUT)

risk = (
    df.groupby("oblast")
      .agg(
          avg_alert_hours_per_day=("alert_hours", "mean"),
          median_alert_hours=("alert_hours", "median"),
          max_alert_hours=("alert_hours", "max"),
          alert_day_probability=("alert_hours", lambda x: (x > 0).mean() * 100),
      )
      .reset_index()
)

risk = risk.sort_values(
    "avg_alert_hours_per_day",
    ascending=False
)

risk["rank"] = range(1, len(risk) + 1)

risk["avg_alert_hours_per_day"] = risk["avg_alert_hours_per_day"].round(2)
risk["median_alert_hours"] = risk["median_alert_hours"].round(2)
risk["alert_day_probability"] = risk["alert_day_probability"].round(1)

risk = risk[
    [
        "rank",
        "oblast",
        "avg_alert_hours_per_day",
        "median_alert_hours",
        "max_alert_hours",
        "alert_day_probability",
    ]
]

print("\nREGIONAL RISK INDEX\n")
print(risk)

risk.to_csv(OUTPUT, index=False)

print("\nSaved:")
print(OUTPUT)