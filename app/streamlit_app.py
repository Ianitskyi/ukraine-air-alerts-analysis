import json

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Ukraine Air Alerts Atlas",
    page_icon="⚠️",
    layout="wide",
)

if "lang" not in st.session_state:
    st.session_state.lang = "uk"

GITHUB_URL = "https://github.com/Ianitskyi/ukraine-air-alerts-analysis"
DATASET_URL = "https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset"
ALERTS_IN_UA_URL = "https://alerts.in.ua/"
AIR_ALARMS_URL = "https://air-alarms.in.ua/"
AJAX_URL = "https://ajax.systems/blog/air-alert-fourth-anniversary/"

TEXT = {
    "uk": {
        "switch": "EN",
        "title": "Атлас повітряних тривог України",
        "subtitle": "Історичний аналіз повітряних тривог за регіонами України на основі відкритих даних.",
        "select_region": "Оберіть регіон",
        "all": "Вся Україна",
        "prob": "Ймовірність дня з тривогою",
        "avg_region": "Середньо годин тривоги на день",
        "avg_national": "Середньо регіон-годин тривоги на день",
        "rank": "Місце серед регіонів",
        "peak_month": "Найінтенсивніший місяць",
        "map": "Карта ризику повітряних тривог",
        "monthly": "Помісячний історичний патерн",
        "heat": "Теплова карта: рік × місяць",
        "conclusions": "Аналітичні висновки",
        "limitations": "Обмеження, авторство і джерела",
        "month": "Місяць",
        "year": "Рік",
        "excluded": "Не включено до аналізу",
        "map_note": "Карта показує історичну ймовірність того, що в регіоні протягом календарного дня була хоча б одна повітряна тривога. Дані усереднені за весь доступний період спостережень.",
        "monthly_note": "Показано середню кількість годин тривоги на день для кожного місяця, усереднену за всі роки спостережень.",
        "heat_note": "Кожна комірка показує середню кількість годин тривоги на день у відповідному місяці.",
    },
    "en": {
        "switch": "УКР",
        "title": "Ukraine Air Alerts Atlas",
        "subtitle": "Historical analysis of air raid alerts across Ukrainian regions based on open data.",
        "select_region": "Select region",
        "all": "All Ukraine",
        "prob": "Alert-day probability",
        "avg_region": "Average alert-hours per day",
        "avg_national": "Average regional alert-hours per day",
        "rank": "National rank",
        "peak_month": "Most intensive month",
        "map": "Air alert risk map",
        "monthly": "Monthly historical pattern",
        "heat": "Year × month heat map",
        "conclusions": "Analytical conclusions",
        "limitations": "Limitations, authorship and sources",
        "month": "Month",
        "year": "Year",
        "excluded": "Excluded from analysis",
        "map_note": "The map shows the historical probability that a region had at least one air raid alert during a calendar day. Values are averaged across the full available observation period.",
        "monthly_note": "Shows the average number of alert-hours per day for each month, averaged across all observed years.",
        "heat_note": "Each cell shows the average number of alert-hours per day in the corresponding month.",
    },
}

MONTHS = {
    "uk": {
        1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
        5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
        9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень",
    },
    "en": {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    },
}

lang = st.session_state.lang
t = TEXT[lang]


def fmt(value):
    if pd.isna(value):
        return "—"
    text = f"{float(value):.1f}"
    return text.replace(".", ",") if lang == "uk" else text


def section_title(base, selected_display):
    return f"{base}: {selected_display}"


def add_geometry_outline(fig, geometry, color="#FFFFFF", width=4.5):
    if geometry.geom_type == "Polygon":
        polygons = [geometry]
    elif geometry.geom_type == "MultiPolygon":
        polygons = list(geometry.geoms)
    else:
        polygons = []

    for polygon in polygons:
        lon, lat = polygon.exterior.xy
        fig.add_trace(
            go.Scattermapbox(
                lon=list(lon),
                lat=list(lat),
                mode="lines",
                line=dict(color=color, width=width),
                hoverinfo="skip",
                showlegend=False,
            )
        )


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        max-width: 1180px;
    }
    h1 {
        font-size: 3rem !important;
        letter-spacing: -1.4px;
        line-height: 1.05;
    }
    .subtitle {
        font-size: 1.15rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    .note {
        font-size: .95rem;
        color: #6b7280;
        margin-top: -.4rem;
        margin-bottom: .9rem;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
    }
    div[data-baseweb="select"] {
        max-width: 460px;
    }
    div[data-baseweb="select"] > div {
        background-color: #e2e8f0;
        border-radius: 14px;
        border: 1px solid #cbd5e1;
    }
    .stButton button {
        border-radius: 999px;
    }
    @media (max-width: 700px) {
        h1 {
            font-size: 2.05rem !important;
        }
        .subtitle {
            font-size: 1rem;
        }
        div[data-baseweb="select"] {
            max-width: 100%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([8, 1])

with top_left:
    st.title(t["title"])
    st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)

st.info(
    "📱 Для зручного перегляду карт і теплових діаграм на смартфоні поверніть екран горизонтально."
    if lang == "uk"
    else "📱 For better viewing of maps and heatmaps on a smartphone, please rotate your screen horizontally."
)

with top_right:
    st.write("")
    if st.button(t["switch"], use_container_width=True):
        st.session_state.lang = "en" if lang == "uk" else "uk"
        st.rerun()

risk = pd.read_csv("outputs/tables/regional_risk_index.csv")
daily_region = pd.read_csv("data/processed/daily_region_alert_hours.csv")
regional_month = pd.read_csv("outputs/tables/regional_month_patterns.csv")
year_month = pd.read_csv("outputs/tables/year_month_heatmap.csv", index_col=0)
gdf = gpd.read_file("outputs/tables/map_dataset.geojson")

daily_region["date"] = pd.to_datetime(daily_region["date"])
daily_region["year"] = daily_region["date"].dt.year

gdf["display_name"] = gdf["uk_name"] if lang == "uk" else gdf["en_name"]
name_map = dict(zip(gdf["dataset_name"], gdf["display_name"]))
risk["display_name"] = risk["oblast"].map(name_map).fillna(risk["oblast"])

region_options = [t["all"]] + list(risk["display_name"])

selected_display = st.selectbox(t["select_region"], region_options)

selected_region = None
if selected_display != t["all"]:
    selected_region = risk.loc[risk["display_name"] == selected_display, "oblast"].iloc[0]

if selected_region:
    row = risk[risk["oblast"] == selected_region].iloc[0]
    avg_value = row["avg_alert_hours_per_day"]
    prob_value = row["alert_day_probability"]
    rank_value = f"#{int(row['rank'])}"
else:
    national_daily = daily_region.groupby("date")["alert_hours"].sum()
    avg_value = national_daily.mean()
    prob_value = (national_daily > 0).mean() * 100
    rank_value = "—"

if selected_region:
    chart_month = regional_month[regional_month["oblast"] == selected_region].copy()
else:
    chart_month = (
        daily_region.groupby("month")
        .agg(avg_alert_hours_per_day=("alert_hours", "mean"))
        .reset_index()
    )

chart_month["month_name"] = chart_month["month"].map(MONTHS[lang])
chart_month["label"] = chart_month["avg_alert_hours_per_day"].round(1)

max_month = chart_month.loc[chart_month["avg_alert_hours_per_day"].idxmax()]
min_month = chart_month.loc[chart_month["avg_alert_hours_per_day"].idxmin()]

avg_label = t["avg_region"] if selected_region else t["avg_national"]

st.divider()

m1, m2, m3 = st.columns(3)
m1.metric(t["prob"], f"{fmt(prob_value)}%")
m2.metric(avg_label, fmt(avg_value))
m3.metric(t["peak_month"] if not selected_region else t["rank"], max_month["month_name"] if not selected_region else rank_value)

st.header(section_title(t["map"], selected_display))
st.markdown(f"<div class='note'>{t['map_note']}</div>", unsafe_allow_html=True)

gdf["id"] = gdf.index.astype(str)
analyzed = gdf[gdf["status"] != "excluded"].copy()
excluded = gdf[gdf["status"] == "excluded"].copy()
geojson = json.loads(gdf.to_json())

fig_map = go.Figure()

fig_map.add_trace(
    go.Choroplethmapbox(
        geojson=geojson,
        locations=analyzed["id"],
        z=analyzed["alert_day_probability"],
        featureidkey="properties.id",
        colorscale="YlOrRd",
        marker_opacity=0.88,
        marker_line_width=0.8,
        marker_line_color="white",
        colorbar_title=t["prob"],
        customdata=analyzed[
            ["display_name", "alert_day_probability", "avg_alert_hours_per_day", "rank"]
        ],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            + t["prob"] + ": %{customdata[1]:.1f}%<br>"
            + t["avg_region"] + ": %{customdata[2]:.1f}<br>"
            + t["rank"] + ": %{customdata[3]}<extra></extra>"
        ),
    )
)

fig_map.add_trace(
    go.Choroplethmapbox(
        geojson=geojson,
        locations=excluded["id"],
        z=[0] * len(excluded),
        featureidkey="properties.id",
        colorscale=[[0, "lightgray"], [1, "lightgray"]],
        showscale=False,
        marker_opacity=0.95,
        marker_line_width=1.3,
        marker_line_color="black",
        customdata=excluded[["display_name"]],
        hovertemplate="<b>%{customdata[0]}</b><br>" + t["excluded"] + "<extra></extra>",
    )
)

if selected_region:
    selected_geometry = gdf.loc[gdf["dataset_name"] == selected_region, "geometry"].iloc[0]
    add_geometry_outline(fig_map, selected_geometry)

fig_map.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=4.7,
    mapbox_center={"lat": 49.0, "lon": 31.3},
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    height=600,
)

st.plotly_chart(fig_map, use_container_width=True)

st.header(section_title(t["monthly"], selected_display))
st.markdown(f"<div class='note'>{t['monthly_note']}</div>", unsafe_allow_html=True)

fig_month = px.line(
    chart_month,
    x="month_name",
    y="avg_alert_hours_per_day",
    markers=True,
    text="label",
    template="plotly_white",
    labels={
        "month_name": t["month"],
        "avg_alert_hours_per_day": avg_label,
    },
)

fig_month.update_traces(
    line_shape="spline",
    line_width=3,
    marker_size=8,
    textposition="top center",
)

fig_month.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig_month, use_container_width=True)

st.header(section_title(t["heat"], selected_display))
st.markdown(f"<div class='note'>{t['heat_note']}</div>", unsafe_allow_html=True)

if selected_region:
    region_heat_source = daily_region[daily_region["oblast"] == selected_region].copy()
    heat_data = (
        region_heat_source.groupby(["year", "month"])
        .agg(avg_alert_hours_per_day=("alert_hours", "mean"))
        .reset_index()
        .pivot(index="year", columns="month", values="avg_alert_hours_per_day")
        .round(1)
    )
else:
    heat_data = year_month.round(1)

fig_heat = px.imshow(
    heat_data,
    aspect="auto",
    color_continuous_scale="YlOrRd",
    text_auto=".1f",
    template="plotly_white",
    labels={
        "x": t["month"],
        "y": t["year"],
        "color": avg_label,
    },
)

fig_heat.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig_heat, use_container_width=True)

st.header(section_title(t["conclusions"], selected_display))

max_month_name = max_month["month_name"]
min_month_name = min_month["month_name"]

if lang == "uk":
    if selected_region:
        st.markdown(
            f"""
**{selected_display}** має ймовірність дня з повітряною тривогою **{fmt(prob_value)}%** і середній історичний рівень **{fmt(avg_value)} годин тривоги на день**. За цими показниками регіон посідає **{rank_value}** серед проаналізованих областей. Це означає, що ризик зіткнутися з тривогою тут не є випадковим фоном, а регулярною частиною історичного безпекового досвіду регіону.

Помісячний профіль показує, що найінтенсивнішим місяцем історично був **{max_month_name}**, а найспокійнішим — **{min_month_name}**. Це не прогноз майбутніх атак, але корисна історична рамка для розуміння того, як змінювалася інтенсивність повітряних тривог у цьому регіоні протягом року.
"""
        )
    else:
        st.markdown(
            f"""
Для **всієї України** карта показує дуже нерівномірний розподіл історичного навантаження тривогами. Найвищі значення концентруються у східних, південних і прикордонних регіонах, тоді як західні області мають значно нижчі середні показники. Це підтверджує, що національна статистика приховує дуже різні регіональні реальності.

Для всієї країни показник **«регіон-годин»** означає суму годин тривоги по всіх проаналізованих регіонах за день. Саме тому він може бути більшим за 24: наприклад, якщо в 10 областях було по 5 годин тривоги, це 50 регіон-годин. Найінтенсивнішим місяцем у середньому був **{max_month_name}**, а найспокійнішим — **{min_month_name}**.
"""
        )
else:
    if selected_region:
        st.markdown(
            f"""
**{selected_display}** has an alert-day probability of **{fmt(prob_value)}%** and a historical average of **{fmt(avg_value)} alert-hours per day**. It ranks **{rank_value}** among analyzed Ukrainian regions. This means that alerts in this region are not occasional background noise, but a regular part of its historical security environment.

The monthly profile shows that the most intensive month historically was **{max_month_name}**, while the calmest was **{min_month_name}**. This is not a forecast, but it provides useful historical context for understanding how alert intensity has varied in this region across the year.
"""
        )
    else:
        st.markdown(
            f"""
For **Ukraine as a whole**, the map shows a highly uneven distribution of historical alert burden. The highest values are concentrated in eastern, southern, and border regions, while western regions have much lower average levels. National-level figures therefore hide very different regional realities.

For the national view, **regional alert-hours** mean the sum of alert-hours across all analyzed regions per day. That is why the value can exceed 24: for example, 10 regions with 5 alert-hours each equal 50 regional alert-hours. The most intensive month on average was **{max_month_name}**, while the calmest was **{min_month_name}**.
"""
        )

st.header(t["limitations"])

if lang == "uk":
    st.markdown(
        f"""
Цей сайт показує **історичні дані**, а не прогноз. Він не оцінює поточну безпекову ситуацію і не може використовуватися як рекомендація для подорожей, роботи, навчання чи ухвалення рішень щодо безпеки. Для актуальної інформації потрібно користуватися офіційними повідомленнями, застосунками повітряної тривоги та інструкціями органів влади.

Автор проєкту — **Андрій Яніцький**. Проєкт створено з використанням інструментів штучного інтелекту в межах відбору до **KSE Agentic AI Summer School**.

**Джерела і корисні посилання:**

- [GitHub репозиторій проєкту]({GITHUB_URL}) — код, структура даних, скрипти аналізу та візуалізації.
- [Ukrainian Air Raid Sirens Dataset]({DATASET_URL}) — основний історичний набір даних про повітряні тривоги в Україні.
- [alerts.in.ua]({ALERTS_IN_UA_URL}) — публічний сервіс з інформацією про актуальні тривоги та історію.
- [air-alarms.in.ua]({AIR_ALARMS_URL}) — публічний проєкт зі статистикою повітряних тривог.
- [Ajax Air Alert app]({AJAX_URL}) — інформація про застосунок «Повітряна тривога» від Ajax.
"""
    )
else:
    st.markdown(
        f"""
This website presents **historical data**, not a forecast. It does not assess the current security situation and must not be used as travel, work, education, or safety advice. For current information, users should rely on official alerts, air-raid alert apps, and instructions from public authorities.

Project author: **Andrii Ianitskyi**. The project was created with AI assistance as part of the selection process for the **KSE Agentic AI Summer School**.

**Sources and useful links:**

- [Project GitHub repository]({GITHUB_URL}) — code, data structure, analysis scripts, and visualizations.
- [Ukrainian Air Raid Sirens Dataset]({DATASET_URL}) — the main historical dataset used in this project.
- [alerts.in.ua]({ALERTS_IN_UA_URL}) — public service with current alerts and historical information.
- [air-alarms.in.ua]({AIR_ALARMS_URL}) — public project with air-alert statistics.
- [Ajax Air Alert app]({AJAX_URL}) — information about the Air Alert app by Ajax.
"""
    )