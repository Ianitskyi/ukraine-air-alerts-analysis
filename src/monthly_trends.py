import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/alerts_oblast_only.csv")

monthly = (
    df.groupby(["year", "month"])
    .agg(
        total_alert_hours=("alert_hours", "sum")
    )
    .reset_index()
)

monthly["period"] = (
    monthly["year"].astype(str)
    + "-"
    + monthly["month"].astype(str).str.zfill(2)
)

plt.figure(figsize=(14, 6))

plt.plot(
    monthly["period"],
    monthly["total_alert_hours"],
    linewidth=2
)

plt.xticks(rotation=90)

plt.title("Total Alert Hours by Month")
plt.ylabel("Alert Hours")
plt.xlabel("Month")

plt.tight_layout()

plt.savefig(
    "outputs/charts/monthly_alert_hours.png",
    dpi=300
)

print("Chart saved:")
print("outputs/charts/monthly_alert_hours.png")