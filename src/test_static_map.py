import geopandas as gpd
import matplotlib.pyplot as plt

INPUT = "outputs/tables/map_dataset.geojson"

gdf = gpd.read_file(INPUT)

analyzed = gdf[gdf["status"] != "excluded"]
excluded = gdf[gdf["status"] == "excluded"]

fig, ax = plt.subplots(figsize=(10, 8))

# analyzed regions
analyzed.plot(
    column="alert_day_probability",
    legend=True,
    ax=ax,
    edgecolor="white",
    linewidth=0.6,
    cmap="YlOrRd"
)

# excluded / occupied regions
excluded.plot(
    ax=ax,
    color="lightgray",
    edgecolor="black",
    linewidth=1.2,
    hatch="///"
)

# labels for excluded regions
for _, row in excluded.iterrows():
    point = row.geometry.representative_point()
    ax.text(
        point.x,
        point.y,
        "Excluded",
        fontsize=8,
        ha="center",
        va="center"
    )

ax.set_title("Ukraine Alert Risk Map")
ax.set_axis_off()

plt.tight_layout()
plt.savefig(
    "outputs/charts/ukraine_static_risk_map.png",
    dpi=300
)

plt.show()