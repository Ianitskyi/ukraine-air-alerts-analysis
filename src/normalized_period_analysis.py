import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/oblast_alert_hours.csv")

# Each row = 1 oblast-hour with alert active
# First calculate daily totals
daily = (
    df.groupby(["date"])
      .size()
      .reset_index(name="alert_hours")
)

daily["date"] = pd.to_datetime(daily["date"])
daily["year"] = daily["date"].dt.year
daily["month"] = daily["date"].dt.month
daily["weekday"] = daily["date"].dt.day_name()
daily["hour"] = None

# Month averages: average alert-hours per day by month
monthly_avg = (
    daily.groupby("month")
         .agg(
             avg_alert_hours_per_day=("alert_hours", "mean"),
             days_observed=("date", "count")
         )
         .reset_index()
)

# Weekday averages: average alert-hours per day by weekday
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

weekday_avg = (
    daily.groupby("weekday")
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

# Save tables
monthly_avg.to_csv("outputs/tables/monthly_average_alert_hours.csv", index=False)
weekday_avg.to_csv("outputs/tables/weekday_average_alert_hours.csv", index=False)

print("\nMONTHLY AVERAGE ALERT-HOURS PER DAY")
print(monthly_avg)

print("\nWEEKDAY AVERAGE ALERT-HOURS PER DAY")
print(weekday_avg)

# Monthly chart
plt.figure(figsize=(10, 5))
plt.bar(monthly_avg["month"], monthly_avg["avg_alert_hours_per_day"])
plt.title("Average Alert-Hours per Day by Month")
plt.xlabel("Month")
plt.ylabel("Average Alert-Hours per Day")
plt.tight_layout()
plt.savefig("outputs/charts/monthly_average_alert_hours.png", dpi=300)

# Weekday chart
plt.figure(figsize=(10, 5))
plt.bar(weekday_avg["weekday"], weekday_avg["avg_alert_hours_per_day"])
plt.title("Average Alert-Hours per Day by Weekday")
plt.xlabel("Weekday")
plt.ylabel("Average Alert-Hours per Day")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/charts/weekday_average_alert_hours.png", dpi=300)

print("\nSaved:")
print("outputs/tables/monthly_average_alert_hours.csv")
print("outputs/tables/weekday_average_alert_hours.csv")
print("outputs/charts/monthly_average_alert_hours.png")
print("outputs/charts/weekday_average_alert_hours.png")