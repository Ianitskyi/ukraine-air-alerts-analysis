from pathlib import Path
import pandas as pd
import geopandas as gpd

GEOJSON = "data/reference/ukraine_oblasts.geojson"
MAPPING = "data/reference/region_mapping.csv"
REGIONS = "data/reference/regions.csv"
RISK = "outputs/tables/regional_risk_index.csv"

OUTPUT_CSV = "outputs/tables/map_dataset.csv"
OUTPUT_GEOJSON = "outputs/tables/map_dataset.geojson"

EXCLUDED = ["Crimea", "Sevastopol", "Luhanska oblast"]

print("Loading files...")

geo = gpd.read_file(GEOJSON)
mapping = pd.read_csv(MAPPING)
regions = pd.read_csv(REGIONS)
risk = pd.read_csv(RISK)

print("Preparing GeoJSON names...")

geo = geo.rename(columns={"shapeName": "geojson_name"})

geo = geo.merge(
    mapping,
    on="geojson_name",
    how="left"
)

print("Merging risk data...")

geo = geo.merge(
    risk,
    left_on="dataset_name",
    right_on="oblast",
    how="left"
)

geo = geo.merge(
    regions,
    left_on="dataset_name",
    right_on="dataset_oblast",
    how="left"
)

geo["status"] = geo["status"].fillna("unknown")

# Force occupied/excluded regions to remain visible but not analyzed
geo.loc[
    geo["dataset_name"].isin(EXCLUDED),
    "status"
] = "excluded"

# Risk categories based on probability of at least one alert day
def risk_category(row):
    if row["status"] == "excluded":
        return "Excluded"
    if pd.isna(row["alert_day_probability"]):
        return "No data"

    p = row["alert_day_probability"]

    if p >= 90:
        return "Very high"
    if p >= 70:
        return "High"
    if p >= 50:
        return "Medium"
    if p >= 30:
        return "Low"
    return "Very low"


geo["risk_category"] = geo.apply(risk_category, axis=1)

# Keep clean columns for CSV preview
csv_columns = [
    "geojson_name",
    "dataset_name",
    "en_name",
    "uk_name",
    "status",
    "rank",
    "avg_alert_hours_per_day",
    "median_alert_hours",
    "max_alert_hours",
    "alert_day_probability",
    "risk_category",
]

Path("outputs/tables").mkdir(parents=True, exist_ok=True)

geo[csv_columns].to_csv(OUTPUT_CSV, index=False)

geo.to_file(OUTPUT_GEOJSON, driver="GeoJSON")

print("\nMap dataset created.")
print(f"CSV: {OUTPUT_CSV}")
print(f"GeoJSON: {OUTPUT_GEOJSON}")

print("\nPreview:")
print(
    geo[
        [
            "geojson_name",
            "dataset_name",
            "status",
            "avg_alert_hours_per_day",
            "alert_day_probability",
            "risk_category",
        ]
    ].sort_values("geojson_name")
)

print("\nUnmatched GeoJSON regions:")
print(
    geo[geo["dataset_name"].isna()][["geojson_name"]]
)