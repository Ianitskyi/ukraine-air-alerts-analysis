import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/daily_alert_hours.csv")

weekday_order = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

monthly_avg = (
    df.groupby("month")
      .agg(
          avg_alert_hours_per_day=("alert_hours", "mean"),
          days_observed=("date", "count")
      )
      .reset_index()
)

weekday_avg = (
    df.groupby("weekday")
      .agg(
          avg_alert_hours_per_day=("alert_hours", "mean"),
          days_observed=("date", "count")
      )
      .reset_index()
)

weekday_avg["weekday"] = pd.Categorical(
    weekday_avg["weekday"],
    categories=weekday_order,
    ordered=True
)

weekday_avg = weekday_avg.sort_values("weekday")

print("\nMONTHLY AVERAGE ALERT-HOURS PER DAY")
print(monthly_avg)

print("\nWEEKDAY AVERAGE ALERT-HOURS PER DAY")
print(weekday_avg)

monthly_avg.to_csv("outputs/tables/monthly_average_daily.csv", index=False)
weekday_avg.to_csv("outputs/tables/weekday_average_daily.csv", index=False)

plt.figure(figsize=(10, 5))
plt.bar(monthly_avg["month"], monthly_avg["avg_alert_hours_per_day"])
plt.title("Average Daily Alert-Hours by Month")
plt.xlabel("Month")
plt.ylabel("Average Alert-Hours per Day")
plt.tight_layout()
plt.savefig("outputs/charts/monthly_average_daily.png", dpi=300)

plt.figure(figsize=(10, 5))
plt.bar(weekday_avg["weekday"], weekday_avg["avg_alert_hours_per_day"])
plt.title("Average Daily Alert-Hours by Weekday")
plt.xlabel("Weekday")
plt.ylabel("Average Alert-Hours per Day")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/charts/weekday_average_daily.png", dpi=300)

print("\nSaved normalized outputs.")