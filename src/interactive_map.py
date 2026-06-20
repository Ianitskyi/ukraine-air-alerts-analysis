import json
import geopandas as gpd
import plotly.express as px

INPUT = "outputs/tables/map_dataset.geojson"
OUTPUT = "outputs/charts/ukraine_risk_map.html"

gdf = gpd.read_file(INPUT)
gdf["id"] = gdf.index.astype(str)

geojson = json.loads(gdf.to_json())

fig = px.choropleth_map(
    gdf,
    geojson=geojson,
    locations="id",
    featureidkey="properties.id",
    color="alert_day_probability",
    hover_name="en_name",
    hover_data={
        "risk_category": True,
        "alert_day_probability": ":.1f",
        "avg_alert_hours_per_day": ":.2f",
        "rank": True,
        "status": True,
    },
    color_continuous_scale="YlOrRd",
    map_style="carto-positron",
    zoom=5,
    center={"lat": 49.0, "lon": 31.0},
    opacity=0.85,
)

fig.update_layout(
    title="Probability of Alert Day by Region",
    margin=dict(l=0, r=0, t=45, b=0),
)

fig.write_html(OUTPUT)

print("Saved:")
print(OUTPUT)