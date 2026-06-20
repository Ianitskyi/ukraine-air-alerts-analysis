import geopandas as gpd
import pandas as pd

GEOJSON = "data/reference/ukraine_oblasts.geojson"
REGIONS = "data/reference/regions.csv"

geo = gpd.read_file(GEOJSON)
regions = pd.read_csv(REGIONS)

print("\nGeoJSON columns:")
print(geo.columns)

print("\nFirst rows:")
print(geo.head())

print("\nRegion names from GeoJSON:")
for name in sorted(geo["shapeName"].dropna().unique()):
    print("-", name)

print("\nRegions from our CSV:")
for name in regions["en_name"]:
    print("-", name)