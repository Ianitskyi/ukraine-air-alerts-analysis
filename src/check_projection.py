import geopandas as gpd

gdf = gpd.read_file(
    "outputs/tables/map_dataset.geojson"
)

print(gdf.crs)