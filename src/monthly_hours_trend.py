import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/oblast_alert_hours.csv")

monthly = (
    df.groupby(["year", "month"])
    .size()
    .reset_index(name="alert_hours")
)

monthly["period"] = (
    monthly["year"].astype(str)
    + "-"
    + monthly["month"].astype(str).str.zfill(2)
)

plt.figure(figsize=(14, 6))

plt.plot(
    monthly["period"],
    monthly["alert_hours"],
    linewidth=2
)

plt.xticks(rotation=90)

plt.title("Oblast Alert Hours by Month")
plt.ylabel("Alert Hours")
plt.xlabel("Month")

plt.tight_layout()

plt.savefig(
    "outputs/charts/monthly_oblast_alert_hours.png",
    dpi=300
)

print("Chart saved:")
print("outputs/charts/monthly_oblast_alert_hours.png")

print("\nTop months:")
print(
    monthly.sort_values(
        "alert_hours",
        ascending=False
    ).head(10)
)