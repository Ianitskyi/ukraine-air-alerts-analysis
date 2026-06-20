import pandas as pd
import matplotlib.pyplot as plt

month_order = [
    1,2,3,4,5,6,
    7,8,9,10,11,12
]

month_names = {
    1:"Jan",
    2:"Feb",
    3:"Mar",
    4:"Apr",
    5:"May",
    6:"Jun",
    7:"Jul",
    8:"Aug",
    9:"Sep",
    10:"Oct",
    11:"Nov",
    12:"Dec"
}

df = pd.read_csv("data/processed/oblast_alert_hours.csv")

seasonality = (
    df.groupby("month")
      .size()
      .reset_index(name="alert_hours")
)

seasonality["month"] = pd.Categorical(
    seasonality["month"],
    categories=month_order,
    ordered=True
)

seasonality = seasonality.sort_values("month")

seasonality["month_name"] = (
    seasonality["month"]
    .map(month_names)
)

print("\nALERT HOURS BY MONTH\n")
print(seasonality)

seasonality.to_csv(
    "outputs/tables/month_seasonality.csv",
    index=False
)

plt.figure(figsize=(10,5))

plt.bar(
    seasonality["month_name"],
    seasonality["alert_hours"]
)

plt.title("Alert Hours by Month of Year")
plt.ylabel("Alert Hours")

plt.tight_layout()

plt.savefig(
    "outputs/charts/month_seasonality.png",
    dpi=300
)

print("\nSaved:")
print("outputs/charts/month_seasonality.png")