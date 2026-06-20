import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

INPUT = "data/processed/daily_region_alert_hours.csv"

print("Loading data...")

df = pd.read_csv(INPUT)

# National daily burden
daily = (
    df.groupby("date")
      .agg(
          alert_hours=("alert_hours", "sum")
      )
      .reset_index()
)

daily["date"] = pd.to_datetime(daily["date"])

daily["year"] = daily["date"].dt.year
daily["month"] = daily["date"].dt.month

# Average daily alert-hours for each month-year
heatmap_data = (
    daily.groupby(["year", "month"])
         .agg(
             avg_alert_hours_per_day=("alert_hours", "mean")
         )
         .reset_index()
)

pivot = heatmap_data.pivot(
    index="year",
    columns="month",
    values="avg_alert_hours_per_day"
)

print("\nHEATMAP TABLE\n")
print(pivot.round(1))

pivot.to_csv(
    "outputs/tables/year_month_heatmap.csv"
)

plt.figure(figsize=(12, 5))

sns.heatmap(
    pivot,
    annot=True,
    fmt=".0f",
    cmap="YlOrRd"
)

plt.title(
    "Average Daily Alert-Hours by Year and Month"
)

plt.tight_layout()

plt.savefig(
    "outputs/charts/year_month_heatmap.png",
    dpi=300
)

print("\nSaved:")
print("outputs/charts/year_month_heatmap.png")
print("outputs/tables/year_month_heatmap.csv")