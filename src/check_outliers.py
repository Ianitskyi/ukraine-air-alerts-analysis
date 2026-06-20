import pandas as pd

df = pd.read_csv("data/processed/alerts_oblast_only.csv")

longest = df.sort_values("alert_hours", ascending=False).head(30)

print("Longest alerts:")
print(longest[["oblast", "started_at_kyiv", "finished_at_kyiv", "duration_minutes", "alert_hours"]])

print("\nAlerts longer than 24 hours:", (df["alert_hours"] > 24).sum())
print("Alerts longer than 48 hours:", (df["alert_hours"] > 48).sum())
print("Alerts longer than 72 hours:", (df["alert_hours"] > 72).sum())