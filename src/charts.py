import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("outputs/tables/region_ranking.csv")

top10 = df.head(10)

plt.figure(figsize=(12, 6))
plt.bar(top10["oblast"], top10["total_alert_hours"])

plt.xticks(rotation=45, ha="right")
plt.title("Top Regions by Total Alert Hours")
plt.ylabel("Alert Hours")

plt.tight_layout()

plt.savefig(
    "outputs/charts/top_regions_alert_hours.png",
    dpi=300
)

print("Chart saved:")
print("outputs/charts/top_regions_alert_hours.png")