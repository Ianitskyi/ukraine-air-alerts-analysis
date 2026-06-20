import pandas as pd
import matplotlib.pyplot as plt

INPUT = "data/processed/daily_region_alert_hours.csv"

df = pd.read_csv(INPUT)

yearly = (
    df.groupby(["oblast", "year"])
      .agg(
          avg_alert_hours_per_day=("alert_hours", "mean")
      )
      .reset_index()
)

pivot = yearly.pivot(
    index="oblast",
    columns="year",
    values="avg_alert_hours_per_day"
)

pivot = pivot.round(2)

print("\nREGIONAL YEARLY TRENDS")
print(pivot)

pivot.to_csv("outputs/tables/regional_yearly_trends.csv")

# Top 8 regions by 2026 average
top_regions = (
    yearly[yearly["year"] == yearly["year"].max()]
    .sort_values("avg_alert_hours_per_day", ascending=False)
    .head(8)["oblast"]
)

chart_data = yearly[yearly["oblast"].isin(top_regions)]

plt.figure(figsize=(12, 6))

for oblast in top_regions:
    region_data = chart_data[chart_data["oblast"] == oblast]
    plt.plot(
        region_data["year"],
        region_data["avg_alert_hours_per_day"],
        marker="o",
        label=oblast
    )

plt.title("Regional Trends: Average Alert-Hours per Day")
plt.xlabel("Year")
plt.ylabel("Average Alert-Hours per Day")
plt.legend()
plt.tight_layout()

plt.savefig("outputs/charts/regional_yearly_trends.png", dpi=300)

print("\nSaved:")
print("outputs/tables/regional_yearly_trends.csv")
print("outputs/charts/regional_yearly_trends.png")