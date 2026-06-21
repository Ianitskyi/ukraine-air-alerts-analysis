import json
from datetime import date

import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


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
        "subtitle": "Історичний аналіз повітряних тривог за регіонами України.",
        "all": "Вся Україна",
        "travel": "Я планую поїхати до",
        "from_day": "День початку",
        "from_month": "Місяць початку",
        "to_day": "День завершення",
        "to_month": "Місяць завершення",
        "prob": "Ймовірність дня з тривогою",
        "avg": "Середньо годин тривоги на день",
        "median": "Медіана годин тривоги на день",
        "rank": "Місце серед регіонів",
        "map": "Теплова карта України",
        "monthly": "Помісячний історичний патерн",
        "period": "Обрані дати в історичному контексті",
        "heat": "Теплова карта: рік × місяць",
        "conclusions": "Аналітичні висновки",
        "limitations": "Обмеження, авторство і джерела",
        "month": "Місяць",
        "year": "Рік",
        "day": "День року",
        "hours": "Години тривоги",
        "excluded": "Не включено до аналізу",
        "map_note": "Колір показує ймовірність того, що в регіоні протягом дня була хоча б одна повітряна тривога. Обраний регіон виділено контуром.",
        "monthly_note": "Показано середню кількість годин тривоги на день для кожного місяця, усереднену за всі роки спостережень.",
        "period_note": "Показано денну динаміку тривог у різні роки. Обраний календарний період підсвічено; графік можна масштабувати й прокручувати.",
        "heat_note": "Кожна комірка показує середню кількість регіональних годин тривоги на день у відповідному місяці.",
    },
    "en": {
        "switch": "УКР",
        "title": "Ukraine Air Alerts Atlas",
        "subtitle": "Historical analysis of air raid alerts across Ukrainian regions.",
        "all": "All Ukraine",
        "travel": "I’m planning to travel to",
        "from_day": "Start day",
        "from_month": "Start month",
        "to_day": "End day",
        "to_month": "End month",
        "prob": "Alert-day probability",
        "avg": "Average alert-hours per day",
        "median": "Median alert-hours per day",
        "rank": "National rank",
        "map": "Ukraine heat map",
        "monthly": "Monthly historical pattern",
        "period": "Selected dates in historical context",
        "heat": "Year × month heat map",
        "conclusions": "Analytical conclusions",
        "limitations": "Limitations, authorship and sources",
        "month": "Month",
        "year": "Year",
        "day": "Day of year",
        "hours": "Alert-hours",
        "excluded": "Excluded from analysis",
        "map_note": "Color shows the probability that a region had at least one alert on a given day. The selected region is outlined.",
        "monthly_note": "Shows the average number of alert-hours per day for each month, averaged across all observed years.",
        "period_note": "Shows daily alert dynamics across years. The selected calendar period is highlighted; the chart can be zoomed and panned.",
        "heat_note": "Each cell shows the average number of regional alert-hours per day in the corresponding month.",
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


def period_filter(df, start_md, end_md):
    if start_md <= end_md:
        return df[(df["month_day"] >= start_md) & (df["month_day"] <= end_md)]
    return df[(df["month_day"] >= start_md) | (df["month_day"] <= end_md)]


def section_title(base, selected_display):
    return f"{base}: {selected_display}"


def day_of_year(month, day):
    return pd.Timestamp(year=2024, month=month, day=day).dayofyear


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
    .brand-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.2rem;
        height: 2.2rem;
        border: 2px solid #b91c1c;
        color: #b91c1c;
        border-radius: 10px;
        font-size: 1.35rem;
        font-weight: 800;
        margin-right: .55rem;
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
    .source-card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: .8rem;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
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
    }
    </style>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([8, 1])
with top_left:
    st.markdown(
        f"<h1><span class='brand-icon'>!</span>{t['title']}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)

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
daily_region["month_day"] = daily_region["date"].dt.strftime("%m-%d")
daily_region["year"] = daily_region["date"].dt.year
daily_region["day_of_year"] = daily_region["date"].dt.dayofyear

gdf["display_name"] = gdf["uk_name"] if lang == "uk" else gdf["en_name"]
name_map = dict(zip(gdf["dataset_name"], gdf["display_name"]))
risk["display_name"] = risk["oblast"].map(name_map).fillna(risk["oblast"])

region_options = [t["all"]] + list(risk["display_name"])

today = date.today()
default_end_day = min(today.day + 14, 28)

f1, f2, f3, f4, f5 = st.columns([2.3, 1, 1.3, 1, 1.3])

with f1:
    selected_display = st.selectbox(t["travel"], region_options)

with f2:
    start_day = st.selectbox(t["from_day"], list(range(1, 32)), index=today.day - 1)

with f3:
    start_month_label = st.selectbox(
        t["from_month"],
        list(MONTHS[lang].values()),
        index=today.month - 1,
    )

with f4:
    end_day = st.selectbox(t["to_day"], list(range(1, 32)), index=default_end_day - 1)

with f5:
    end_month_label = st.selectbox(
        t["to_month"],
        list(MONTHS[lang].values()),
        index=today.month - 1,
    )

month_to_number = {v: k for k, v in MONTHS[lang].items()}
start_month = month_to_number[start_month_label]
end_month = month_to_number[end_month_label]

start_md = f"{start_month:02d}-{start_day:02d}"
end_md = f"{end_month:02d}-{end_day:02d}"
start_doy = day_of_year(start_month, start_day)
end_doy = day_of_year(end_month, end_day)

selected_region = None
if selected_display != t["all"]:
    selected_region = risk.loc[risk["display_name"] == selected_display, "oblast"].iloc[0]

if selected_region:
    row = risk[risk["oblast"] == selected_region].iloc[0]
    avg_value = row["avg_alert_hours_per_day"]
    prob_value = row["alert_day_probability"]
    median_value = row["median_alert_hours"]
    rank_value = f"#{int(row['rank'])}"
else:
    national_daily = daily_region.groupby("date")["alert_hours"].sum()
    avg_value = national_daily.mean()
    prob_value = (national_daily > 0).mean() * 100
    median_value = national_daily.median()
    rank_value = "—"

st.divider()

m1, m2, m3, m4 = st.columns(4)
m1.metric(t["prob"], f"{fmt(prob_value)}%")
m2.metric(t["avg"], fmt(avg_value))
m3.metric(t["median"], fmt(median_value))
m4.metric(t["rank"], rank_value)

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
            + t["avg"] + ": %{customdata[2]:.1f}<br>"
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
    selected_gdf = gdf[gdf["dataset_name"] == selected_region].copy()
    fig_map.add_trace(
        go.Choroplethmapbox(
            geojson=geojson,
            locations=selected_gdf["id"],
            z=[1] * len(selected_gdf),
            featureidkey="properties.id",
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            showscale=False,
            marker_opacity=0.05,
            marker_line_width=4,
            marker_line_color="#111827",
            hoverinfo="skip",
        )
    )

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

fig_month = px.line(
    chart_month,
    x="month_name",
    y="avg_alert_hours_per_day",
    markers=True,
    text="label",
    template="plotly_white",
    labels={
        "month_name": t["month"],
        "avg_alert_hours_per_day": t["avg"],
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

st.header(section_title(t["period"], selected_display))
st.markdown(f"<div class='note'>{t['period_note']}</div>", unsafe_allow_html=True)

year_context = daily_region.copy()

if selected_region:
    year_context = year_context[year_context["oblast"] == selected_region]
else:
    year_context = (
        year_context.groupby(["date", "year", "day_of_year", "month_day"])
        .agg(alert_hours=("alert_hours", "sum"))
        .reset_index()
    )

year_context["alert_hours"] = year_context["alert_hours"].round(1)

fig_period = px.line(
    year_context,
    x="day_of_year",
    y="alert_hours",
    color="year",
    template="plotly_white",
    labels={
        "day_of_year": t["day"],
        "alert_hours": t["hours"],
        "year": t["year"],
    },
)

fig_period.update_traces(line_shape="spline", line_width=2.2)

if start_doy <= end_doy:
    fig_period.add_vrect(
        x0=start_doy,
        x1=end_doy,
        fillcolor="rgba(185,28,28,0.18)",
        line_width=0,
        layer="below",
    )
    fig_period.update_xaxes(range=[max(1, start_doy - 30), min(366, end_doy + 30)])
else:
    fig_period.add_vrect(
        x0=start_doy,
        x1=366,
        fillcolor="rgba(185,28,28,0.18)",
        line_width=0,
        layer="below",
    )
    fig_period.add_vrect(
        x0=1,
        x1=end_doy,
        fillcolor="rgba(185,28,28,0.18)",
        line_width=0,
        layer="below",
    )

fig_period.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(rangeslider=dict(visible=True)),
)

st.plotly_chart(fig_period, use_container_width=True)

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
        "color": t["avg"],
    },
)

fig_heat.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20))
st.plotly_chart(fig_heat, use_container_width=True)

st.header(t["conclusions"])

period_data = period_filter(year_context.copy(), start_md, end_md)

period_yearly = (
    period_data.groupby("year")
    .agg(alert_hours=("alert_hours", "sum"))
    .reset_index()
)

if len(period_yearly) > 0:
    worst_period_year = int(period_yearly.loc[period_yearly["alert_hours"].idxmax(), "year"])
    worst_period_value = period_yearly["alert_hours"].max()
else:
    worst_period_year = "—"
    worst_period_value = 0

max_month_name = max_month["month_name"]
min_month_name = min_month["month_name"]

if lang == "uk":
    if selected_region:
        st.markdown(
            f"""
**{selected_display}** має ймовірність дня з повітряною тривогою **{fmt(prob_value)}%** і середній історичний рівень **{fmt(avg_value)} годин тривоги на день**. За цими показниками регіон посідає **{rank_value}** серед проаналізованих областей. Це означає, що ризик зіткнутися з тривогою тут не є випадковим фоном, а регулярною частиною історичного безпекового досвіду регіону.

Помісячний профіль показує, що найінтенсивнішим місяцем історично був **{max_month_name}**, а найспокійнішим — **{min_month_name}**. Для обраного календарного періоду найбільше годин тривоги було зафіксовано у **{worst_period_year} році** — **{fmt(worst_period_value)} годин**. Це не прогноз майбутніх атак, але корисна історична рамка для розуміння того, наскільки типовим або нетиповим був цей період у попередні роки.
"""
        )
    else:
        st.markdown(
            f"""
Для **всієї України** карта показує дуже нерівномірний розподіл історичного навантаження тривогами. Найвищі значення концентруються у східних, південних і прикордонних регіонах, тоді як західні області мають значно нижчі середні показники. Це підтверджує, що національна статистика приховує дуже різні регіональні реальності.

Помісячна динаміка свідчить, що сезонні відмінності існують, але вони слабші за відмінності між роками та регіонами. Найінтенсивнішим місяцем у середньому був **{max_month_name}**, а найспокійнішим — **{min_month_name}**. Для обраного календарного періоду найбільше годин тривоги по країні було зафіксовано у **{worst_period_year} році** — **{fmt(worst_period_value)} годин**.
"""
        )
else:
    if selected_region:
        st.markdown(
            f"""
**{selected_display}** has an alert-day probability of **{fmt(prob_value)}%** and a historical average of **{fmt(avg_value)} alert-hours per day**. It ranks **{rank_value}** among analyzed Ukrainian regions. This means that alerts in this region are not occasional background noise, but a regular part of its historical security environment.

The monthly profile shows that the most intensive month historically was **{max_month_name}**, while the calmest was **{min_month_name}**. For the selected calendar period, the highest number of alert-hours was recorded in **{worst_period_year}** — **{fmt(worst_period_value)} hours**. This is not a forecast, but it gives useful historical context for understanding how unusual or typical this period has been in previous years.
"""
        )
    else:
        st.markdown(
            f"""
For **Ukraine as a whole**, the map shows a highly uneven distribution of historical alert burden. The highest values are concentrated in eastern, southern, and border regions, while western regions have much lower average levels. National-level figures therefore hide very different regional realities.

The monthly pattern suggests that seasonality exists, but it is weaker than the differences between years and regions. The most intensive month on average was **{max_month_name}**, while the calmest was **{min_month_name}**. For the selected calendar period, the highest national number of alert-hours was recorded in **{worst_period_year}** — **{fmt(worst_period_value)} hours**.
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