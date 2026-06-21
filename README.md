# Ukraine Air Alerts Analysis
This project analyzes historical air raid alert data in Ukraine by region.

The project was created as part of the selection process for the KSE Agentic AI Summer School.

## Research question

What are the historical regional and temporal patterns of air raid alerts in Ukraine across the full available period?

## Methodology

The project analyzes the full available period without dividing it into separate stages of the war.

The main analytical level is oblast / region level plus Kyiv City.

Crimea, Sevastopol, and Luhansk oblast are excluded from the main analysis.

District-level and hromada-level alerts are aggregated to oblast level.

Alert duration is calculated in hours. If an alert episode lasted less than one hour, it is counted as one hour.

The project analyzes historical patterns only. It does not forecast attacks and must not be used as safety advice.

## Data source

The primary dataset is the Ukrainian Air Raid Sirens Dataset by Vadimkin on GitHub.

## Planned outputs

- cleaned analytical dataset
- regional rankings
- time-series charts
- analytical report
- Streamlit web dashboard
# Ukraine Air Alerts Atlas

Interactive dashboard for analyzing historical air raid alert patterns across Ukrainian regions.

## Live Demo

🌐 Streamlit App:
https://ТУТ_ТВОЄ_ПОСИЛАННЯ.streamlit.app

## GitHub Repository

https://github.com/Ianitskyi/ukraine-air-alerts-analysis

## Data Source

This project uses historical air raid alert data from:
https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset