import json

with open(
    "outputs/tables/map_dataset.geojson",
    encoding="utf-8"
) as f:
    geo = json.load(f)

print("Number of features:")
print(len(geo["features"]))

print("\nFirst feature properties:")
print(geo["features"][0]["properties"])

print("\nFirst feature geometry type:")
print(geo["features"][0]["geometry"]["type"])