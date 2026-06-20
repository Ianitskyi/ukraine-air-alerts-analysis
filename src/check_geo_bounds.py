import geopandas as gpd

gdf = gpd.read_file("outputs/tables/map_dataset.geojson")

print("CRS:", gdf.crs)

print("\nTotal bounds:")
print(gdf.total_bounds)
print("[min longitude, min latitude, max longitude, max latitude]")

print("\nBounds by region:")
for _, row in gdf.iterrows():
    minx, miny, maxx, maxy = row.geometry.bounds
    print(row["geojson_name"], "=>", [round(minx, 3), round(miny, 3), round(maxx, 3), round(maxy, 3)])