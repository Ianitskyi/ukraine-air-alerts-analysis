import json
import geopandas as gpd
import plotly.graph_objects as go

INPUT = "outputs/tables/map_dataset.geojson"
OUTPUT = "outputs/charts/ukraine_interactive_map.html"

LANGUAGE = "uk"  # change to "en" for English

TEXT = {
    "uk": {
        "title": "Ймовірність дня з повітряною тривогою за регіонами",
        "region": "Регіон",
        "probability": "Ймовірність дня з тривогою",
        "avg_hours": "Середньо годин тривоги на день",
        "rank": "Місце в рейтингу",
        "category": "Категорія ризику",
        "excluded": "Не включено в основний аналіз",
        "excluded_note": "Не включено через обмежену зіставність даних",
    },
    "en": {
        "title": "Probability of an Alert Day by Region",
        "region": "Region",
        "probability": "Probability of alert day",
        "avg_hours": "Average alert-hours per day",
        "rank": "Rank",
        "category": "Risk category",
        "excluded": "Excluded from main analysis",
        "excluded_note": "Excluded because of data comparability limitations",
    },
}

t = TEXT[LANGUAGE]

gdf = gpd.read_file(INPUT)

gdf["id"] = gdf.index.astype(str)
gdf["display_name"] = gdf["uk_name"] if LANGUAGE == "uk" else gdf["en_name"]

analyzed = gdf[gdf["status"] != "excluded"].copy()
excluded = gdf[gdf["status"] == "excluded"].copy()

geojson = json.loads(gdf.to_json())

fig = go.Figure()

fig.add_trace(
    go.Choroplethmapbox(
        geojson=geojson,
        locations=analyzed["id"],
        z=analyzed["alert_day_probability"],
        featureidkey="properties.id",
        colorscale="YlOrRd",
        marker_opacity=0.85,
        marker_line_width=0.7,
        marker_line_color="white",
        colorbar_title=t["probability"],
        customdata=analyzed[
            [
                "display_name",
                "risk_category",
                "alert_day_probability",
                "avg_alert_hours_per_day",
                "rank",
            ]
        ],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            + t["category"] + ": %{customdata[1]}<br>"
            + t["probability"] + ": %{customdata[2]:.1f}%<br>"
            + t["avg_hours"] + ": %{customdata[3]:.2f}<br>"
            + t["rank"] + ": %{customdata[4]}<extra></extra>"
        ),
        name=t["probability"],
    )
)

fig.add_trace(
    go.Choroplethmapbox(
        geojson=geojson,
        locations=excluded["id"],
        z=[0] * len(excluded),
        featureidkey="properties.id",
        colorscale=[[0, "lightgray"], [1, "lightgray"]],
        showscale=False,
        marker_opacity=0.95,
        marker_line_width=1.2,
        marker_line_color="black",
        customdata=excluded[["display_name"]],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            + t["excluded"] + "<br>"
            + t["excluded_note"]
            + "<extra></extra>"
        ),
        name=t["excluded"],
    )
)

fig.update_layout(
    title=t["title"],
    mapbox_style="carto-positron",
    mapbox_zoom=4.7,
    mapbox_center={"lat": 49.0, "lon": 31.3},
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
)

fig.write_html(OUTPUT)

print("Saved:")
print(OUTPUT)