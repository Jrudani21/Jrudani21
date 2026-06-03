# 🦠 COVID-19 Dashboard

Interactive Streamlit dashboard powered by [Our World in Data](https://ourworldindata.org/coronavirus) — runs in Docker with a single command.

## Features

- Global KPIs: total cases, deaths, and vaccinations
- Time-series line charts for cases, deaths, and vaccinations
- Choropleth world map (cases per million)
- Country snapshot table with case-fatality % and vaccination rate
- Sidebar filters: continent, country, and date range

## Quick Start (Docker — pre-built image)

The image is automatically built and pushed to GitHub Container Registry on every merge to `main`.

```bash
# Pull and run (no build step needed)
docker run -p 8501:8501 ghcr.io/jrudani21/covid-dashboard:latest

# Open in browser
open http://localhost:8501
```

### With Docker Compose (build locally)

```bash
docker compose up --build
```

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Source

[Our World in Data COVID-19 dataset](https://github.com/owid/covid-19-data) — updated daily, fetched at runtime and cached for 1 hour.
