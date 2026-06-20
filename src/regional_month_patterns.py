import pandas as pd
import matplotlib.pyplot as plt

INPUT = "data/processed/daily_region_alert_hours.csv"

df = pd.read_csv(INPUT)

# Average daily alert-hours by region and month of year
monthly_region = (
    df.groupby(["oblast", "month"])
      .agg(
          avg_alert_hours_per_day=("alert_hours", "mean"),
          days_observed=("date", "count")
      )
      .reset_index()
)

monthly_region.to_csv(
    "outputs/tables/regional_month_patterns.csv",
    index=False
)

print("\nREGIONAL MONTH PATTERNS")
print(monthly_region.head(30))

# Choose several key regions for comparison
selected_regions = [
    "Kyiv City",
    "Kyivska oblast",
    "Odeska oblast",
    "Lvivska oblast",
    "Dnipropetrovska oblast",
    "Kharkivska oblast",
    "Sumska oblast",
    "Zaporizka oblast",
]

chart_data = monthly_region[
    monthly_region["oblast"].isin(selected_regions)
]

plt.figure(figsize=(12, 6))

for oblast in selected_regions:
    region_data = chart_data[chart_data["oblast"] == oblast]
    plt.plot(
        region_data["month"],
        region_data["avg_alert_hours_per_day"],
        marker="o",
        label=oblast
    )

plt.title("Average Daily Alert-Hours by Month and Region")
plt.xlabel("Month")
plt.ylabel("Average Alert-Hours per Day")
plt.xticks(range(1, 13))
plt.legend()
plt.tight_layout()

plt.savefig(
    "outputs/charts/regional_month_patterns.png",
    dpi=300
)

print("\nSaved:")
print("outputs/tables/regional_month_patterns.csv")
print("outputs/charts/regional_month_patterns.png")