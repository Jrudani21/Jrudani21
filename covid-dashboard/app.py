import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🦠",
    layout="wide",
)

DATA_URL = "https://covid.ourworldindata.org/data/owid-covid-data.csv"

COLS = [
    "iso_code", "continent", "location", "date",
    "total_cases", "new_cases", "total_deaths", "new_deaths",
    "total_vaccinations", "people_vaccinated", "people_fully_vaccinated",
    "population",
]


@st.cache_data(ttl=3600, show_spinner="Fetching latest COVID data…")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL, usecols=COLS, parse_dates=["date"], low_memory=False)
    df = df[~df["iso_code"].str.startswith("OWID", na=True)]  # drop aggregates
    df["date"] = pd.to_datetime(df["date"])
    return df


df = load_data()

st.title("🦠 COVID-19 Global Dashboard")
st.caption("Data: Our World in Data · refreshes every hour")

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.header("Filters")

continents = sorted(df["continent"].dropna().unique())
sel_continent = st.sidebar.multiselect("Continent", continents, default=continents)

filtered = df[df["continent"].isin(sel_continent)] if sel_continent else df

countries = sorted(filtered["location"].dropna().unique())
sel_countries = st.sidebar.multiselect(
    "Country / Region", countries, default=["Canada", "United States", "India", "Brazil"]
)

date_min, date_max = df["date"].min().date(), df["date"].max().date()
sel_dates = st.sidebar.date_input("Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
start_date = pd.Timestamp(sel_dates[0])
end_date = pd.Timestamp(sel_dates[1]) if len(sel_dates) == 2 else pd.Timestamp(date_max)

plot_df = df[
    df["location"].isin(sel_countries)
    & df["date"].between(start_date, end_date)
].copy()

# ── KPI row ───────────────────────────────────────────────────────────────────
latest = (
    df[df["date"] == df["date"].max()]
    .groupby("location", as_index=False)
    .first()
)
world_cases = latest["total_cases"].sum()
world_deaths = latest["total_deaths"].sum()
world_vacc = latest["people_fully_vaccinated"].sum()

k1, k2, k3 = st.columns(3)
k1.metric("🌍 Total Cases (global)", f"{world_cases:,.0f}")
k2.metric("💀 Total Deaths (global)", f"{world_deaths:,.0f}")
k3.metric("💉 Fully Vaccinated (global)", f"{world_vacc:,.0f}")

st.divider()

# ── Line charts ───────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Cases", "💀 Deaths", "💉 Vaccinations", "🗺️ World Map"])

with tab1:
    metric = st.radio("Metric", ["new_cases", "total_cases"], horizontal=True, key="cases_m")
    label = "New Cases" if metric == "new_cases" else "Total Cases"
    if plot_df.empty:
        st.info("Select at least one country.")
    else:
        fig = px.line(plot_df, x="date", y=metric, color="location",
                      labels={"date": "Date", metric: label, "location": "Country"},
                      title=f"{label} over time")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    metric = st.radio("Metric", ["new_deaths", "total_deaths"], horizontal=True, key="deaths_m")
    label = "New Deaths" if metric == "new_deaths" else "Total Deaths"
    if plot_df.empty:
        st.info("Select at least one country.")
    else:
        fig = px.line(plot_df, x="date", y=metric, color="location",
                      labels={"date": "Date", metric: label, "location": "Country"},
                      title=f"{label} over time")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    vacc_df = plot_df.dropna(subset=["people_fully_vaccinated"])
    if vacc_df.empty:
        st.info("No vaccination data for the selected countries / range.")
    else:
        fig = px.line(vacc_df, x="date", y="people_fully_vaccinated", color="location",
                      labels={"date": "Date", "people_fully_vaccinated": "Fully Vaccinated", "location": "Country"},
                      title="People Fully Vaccinated over time")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    latest_sel = latest[latest["location"].isin(countries)].copy()
    latest_sel["cases_per_million"] = latest_sel["total_cases"] / latest_sel["population"] * 1e6
    fig = px.choropleth(
        latest_sel,
        locations="iso_code",
        color="cases_per_million",
        hover_name="location",
        hover_data={"total_cases": ":,.0f", "total_deaths": ":,.0f"},
        color_continuous_scale="Reds",
        title="Total Cases per Million (latest date)",
        labels={"cases_per_million": "Cases / million"},
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

# ── Country comparison bar ─────────────────────────────────────────────────────
st.subheader("Country Snapshot (latest date)")
snap = latest[latest["location"].isin(sel_countries)][
    ["location", "total_cases", "total_deaths", "people_fully_vaccinated", "population"]
].copy()
snap["case_fatality_%"] = snap["total_deaths"] / snap["total_cases"] * 100
snap["vacc_%"] = snap["people_fully_vaccinated"] / snap["population"] * 100
st.dataframe(snap.set_index("location").style.format({
    "total_cases": "{:,.0f}", "total_deaths": "{:,.0f}",
    "people_fully_vaccinated": "{:,.0f}", "population": "{:,.0f}",
    "case_fatality_%": "{:.2f}%", "vacc_%": "{:.1f}%",
}), use_container_width=True)
