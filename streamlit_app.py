import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Live Flight Tracker", layout="wide")

st.title("✈️ Live Flight Tracker")

st.write("""
This dashboard fetches **live aircraft positions** from the [OpenSky Network](https://opensky-network.org/).
Explore real-time flights worldwide on an interactive map.
""")

# -------------------------------------------------
# 1. Fetch aircraft positions from OpenSky API
# -------------------------------------------------

@st.cache_data(ttl=60)
def fetch_flights():
    """
    Fetches live aircraft positions from OpenSky Network API.
    Returns a DataFrame.
    """
    url = "https://opensky-network.org/api/states/all"

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
    except Exception as e:
        st.error(f"API request failed: {e}")
        return pd.DataFrame()

    states = data.get("states", [])
    columns = [
        "icao24", "callsign", "origin_country",
        "time_position", "last_contact",
        "longitude", "latitude", "baro_altitude",
        "on_ground", "velocity", "heading",
        "vertical_rate", "sensors", "geo_altitude",
        "squawk", "spi", "position_source"
    ]

    df = pd.DataFrame(states, columns=columns)

    # Keep only planes with valid coordinates
    df = df.dropna(subset=["latitude", "longitude"])

    return df


if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

flights_df = fetch_flights()

st.caption(f"Number of aircraft currently tracked: {len(flights_df)}")

# -------------------------------------------------
# 2. Data Table
# -------------------------------------------------

with st.expander("🔍 View Data Table"):
    st.dataframe(flights_df)

# -------------------------------------------------
# 3. Plotly Map
# -------------------------------------------------

st.subheader("🗺️ Live Aircraft Map")

if not flights_df.empty:
    fig = px.scatter_mapbox(
        flights_df,
        lat="latitude",
        lon="longitude",
        hover_name="callsign",
        hover_data={
            "origin_country": True,
            "baro_altitude": True,
            "velocity": True,
            "heading": True
        },
        color="origin_country",
        size_max=10,
        zoom=2,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No aircraft data available right now.")
