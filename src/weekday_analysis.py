import pandas as pd
import matplotlib.pyplot as plt

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

df = pd.read_csv("data/processed/oblast_alert_hours.csv")

weekday = (
    df.groupby("weekday")
      .size()
      .reset_index(name="alert_hours")
)

weekday["weekday"] = pd.Categorical(
    weekday["weekday"],
    categories=weekday_order,
    ordered=True
)

weekday = weekday.sort_values("weekday")

print("\nALERT HOURS BY WEEKDAY\n")
print(weekday)

weekday.to_csv(
    "outputs/tables/weekday_analysis.csv",
    index=False
)

plt.figure(figsize=(10,5))
plt.bar(
    weekday["weekday"],
    weekday["alert_hours"]
)

plt.title("Alert Hours by Weekday")
plt.ylabel("Alert Hours")

plt.tight_layout()

plt.savefig(
    "outputs/charts/weekday_analysis.png",
    dpi=300
)

print("\nSaved:")
print("outputs/charts/weekday_analysis.png")