import streamlit as st
import requests
import os
from datetime import date, timedelta

st.set_page_config(
    page_title="LunaBase OS | Mission Control",
    page_icon="🌙",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0F172A;
    color: #F8FAFC;
}

h1, h2, h3 {
    color: #38BDF8 !important;
}

[data-testid="stMetric"] {
    background-color: #1E293B;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #334155;
}

[data-testid="stSidebar"] {
    background-color: #17243A;
}

.stButton button {
    background-color: #0284C7;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

.stProgress > div > div > div > div {
    background-color: #10B981;
}
</style>
""", unsafe_allow_html=True)

def show_art(filename, caption=None, width=None):
    if os.path.exists(filename):
        st.image(
            filename,
            caption=caption,
            width=width,
            use_container_width=(width is None)
        )
    else:
        st.info(f"Artwork placeholder: Add {filename} to your project folder.")

@st.cache_data(ttl=3600)
def fetch_solar_flares(api_key):

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    url = "https://api.nasa.gov/DONKI/FLR"

    params = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "api_key": api_key
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=8
        )

        response.raise_for_status()

        events = response.json()

        if events:
            events.sort(
                key=lambda x: x.get("beginTime", ""),
                reverse=True
            )
            return events[0], None

        return None, "No solar flare records found in this period."

    except requests.RequestException as e:
        return None, str(e)

@st.cache_data(ttl=86400)
def fetch_apod(api_key):

    url = "https://api.nasa.gov/planetary/apod"

    try:
        response = requests.get(
            url,
            params={"api_key": api_key},
            timeout=8
        )

        response.raise_for_status()
        return response.json()

    except (requests.RequestException, ValueError):
        return None

defaults = {
    "mission_day": 1,
    "oxygen": 70.0,
    "food": 70.0,
    "crew": 100.0,
    "mission_over": False,
    "mission_success": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

show_art("banner.png")

st.title("🌙 LUNABASE OS")
st.subheader("Junior Astronaut Mission Trainer")

st.markdown(
    "Welcome, Flight Director. Manage your lunar outpost, "
    "protect your crew and keep essential systems operational."
)

st.divider()

st.sidebar.title("🚀 FLIGHT CONTROL")

st.sidebar.markdown("### NASA Connection")

api_key = st.secrets.get("NASA_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input(
        "NASA API Key",
        type="password"
    )

st.sidebar.caption(
    "Use your personal NASA API key or DEMO_KEY."
)

st.sidebar.divider()

st.sidebar.markdown("### ⚡ Power Allocation")

solar_supply = st.sidebar.slider(
    "Solar Array Output (kW)",
    min_value=50,
    max_value=150,
    value=100
)

oxygen_power = st.sidebar.slider(
    "Oxygen Generator (kW)",
    min_value=10,
    max_value=60,
    value=35
)

food_power = st.sidebar.slider(
    "Hydroponics Bay (kW)",
    min_value=10,
    max_value=60,
    value=30
)

shield_power = st.sidebar.slider(
    "Radiation Shielding (kW)",
    min_value=10,
    max_value=80,
    value=25
)

st.sidebar.divider()

st.sidebar.markdown("### ☀️ Mission Conditions")

simulated_storm = st.sidebar.checkbox(
    "Activate simulated solar storm",
    value=False
)

st.sidebar.caption(
    "This is an educational game scenario, "
    "not a real radiation forecast."
)

total_draw = (
    oxygen_power
    + food_power
    + shield_power
)

power_surplus = solar_supply - total_draw

if total_draw > 0:
    power_efficiency = min(
        1.0,
        solar_supply / total_draw
    )
else:
    power_efficiency = 1.0

required_shield = 45 if simulated_storm else 20

power_deficit = power_surplus < 0

st.markdown("## 🛰️ Mission Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Mission Day",
    st.session_state.mission_day
)

col2.metric(
    "Solar Power",
    f"{solar_supply} kW"
)

col3.metric(
    "Power Consumption",
    f"{total_draw} kW"
)

col4.metric(
    "Power Balance",
    f"{power_surplus:+} kW"
)

if power_deficit:
    st.error(
        "⚠️ POWER BLACKOUT RISK: "
        "Your systems require more electricity than the "
        "solar arrays currently produce."
    )
else:
    st.success("POWER GRID: Operating within available capacity.")
st.markdown("## 🏠 Lunar Habitat")

if simulated_storm:
    show_art(
        "hab_alert.png",
        "Solar storm training scenario"
    )
else:
    show_art(
        "hab_nominal.png",
        "Normal lunar habitat operations"
    )

st.markdown("## 📊 Life Support Monitoring")

a, b, c = st.columns(3)

with a:
    st.metric(
        "Oxygen Reserves",
        f"{st.session_state.oxygen:.0f}%"
    )
    st.progress(
        int(max(0, min(100, st.session_state.oxygen)))
    )

with b:
    st.metric(
        "Food Reserves",
        f"{st.session_state.food:.0f}%"
    )
    st.progress(
        int(max(0, min(100, st.session_state.food)))
    )

with c:
    st.metric(
        "Crew Condition",
        f"{st.session_state.crew:.0f}%"
    )
    st.progress(
        int(max(0, min(100, st.session_state.crew)))
    )

st.markdown("## 🚨 Mission Status")

if st.session_state.mission_over:

    if st.session_state.mission_success:
        st.success(
            "🏆 MISSION SUCCESS! "
            "Your crew completed the five-day mission."
        )
    else:
        st.error(
            "MISSION FAILED. Essential resources or "
            "crew conditions became unsustainable."
        )

elif power_deficit:
    st.error("CRITICAL: Your power demand exceeds supply.")

elif (
    st.session_state.oxygen < 30
    or st.session_state.food < 30
    or st.session_state.crew < 50
):
    st.warning("WARNING: One or more resources are running low.")

elif simulated_storm and shield_power < required_shield:
    st.warning(
        "RADIATION WARNING: Increase shielding "
        "to the required level for this scenario."
    )

else:
    st.success("OPERATIONAL: All monitored systems are stable.")

st.divider()

st.markdown("## 🎮 Mission Control")

st.write(
    "Once you are satisfied with your power allocation, "
    "advance the mission by one day."
)

if st.button(
    "🚀 ADVANCE MISSION DAY",
    disabled=st.session_state.mission_over
):

    # Calculate how efficiently available power is used

    efficiency = power_efficiency

    # Oxygen production and consumption

    oxygen_change = (
        (oxygen_power - 30) * 0.7 * efficiency
    )

    # Food production and consumption

    food_change = (
        (food_power - 30) * 0.6 * efficiency
    )

    st.session_state.oxygen = max(
        0,
        min(100, st.session_state.oxygen + oxygen_change)
    )

    st.session_state.food = max(
        0,
        min(100, st.session_state.food + food_change)
    )

    # Crew condition

    if power_deficit:
        st.session_state.crew -= 8

    if simulated_storm and shield_power < required_shield:
        st.session_state.crew -= 12

    elif not simulated_storm and shield_power < required_shield:
        st.session_state.crew -= 3

    else:
        st.session_state.crew += 2

    st.session_state.crew = max(
        0,
        min(100, st.session_state.crew)
    )

    st.session_state.mission_day += 1

    # Check mission failure

    if (
        st.session_state.oxygen <= 0
        or st.session_state.food <= 0
        or st.session_state.crew <= 0
    ):
        st.session_state.mission_over = True
        st.session_state.mission_success = False

    # Check five-day mission completion

    elif st.session_state.mission_day > 5:

        st.session_state.mission_over = True

        st.session_state.mission_success = (
            st.session_state.oxygen >= 20
            and st.session_state.food >= 20
            and st.session_state.crew >= 50
        )

    st.rerun()


if st.session_state.mission_over:

    if st.session_state.mission_success:
        st.balloons()
        show_art(
            "badge_win.png",
            "Certified Lunar Flight Director"
        )

    else:
        st.error(
            "Your mission has ended. Review your resource "
            "allocation and try again."
        )


if st.button("🔄 RESTART MISSION"):

    for key, value in defaults.items():
        st.session_state[key] = value

    st.rerun()

st.divider()

st.markdown("## ☀️ NASA Space Weather Observatory")

st.write(
    "Latest recorded solar flare information from "
    "NASA's DONKI database."
)

with st.spinner("Connecting to NASA..."):

    flare, flare_error = fetch_solar_flares(api_key)

if flare:

    st.success("NASA DONKI connection successful.")

    f1, f2 = st.columns(2)

    with f1:
        st.metric(
            "Latest Recorded Flare",
            flare.get("classType", "Unknown")
        )

    with f2:
        st.metric(
            "Observation Time",
            flare.get("beginTime", "Unknown")[:10]
        )

    st.write(
        "**Event ID:**",
        flare.get("flrID", "Not available")
    )

    st.caption(
        "This is historical observational information. "
        "It does not establish a current lunar radiation threat."
    )

elif flare_error:
    st.warning(
        "NASA data is currently unavailable. "
        "The rest of the application can still be used."
    )

    st.caption(flare_error)

st.divider()

st.markdown("## 🌌 Mission Briefing")

if st.button("Load NASA Astronomy Picture of the Day"):

    with st.spinner("Retrieving NASA astronomy image..."):

        apod = fetch_apod(api_key)

    if apod:

        st.subheader(apod.get("title", "NASA Astronomy Picture"))

        if apod.get("media_type") == "image":
            st.image(apod["url"], use_container_width=True)

        else:
            st.info(
                "Today's NASA feature is not a still image. "
                "Use the link below to view it."
            )

        st.write(apod.get("explanation", ""))

        if apod.get("media_type") != "image":
            st.markdown(
                f"[View NASA feature]({apod.get('url', '')})"
            )

    else:
        st.warning(
            "Could not retrieve today's astronomy picture. "
            "Please try again later."
        )

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#94A3B8;">
        <h3>LUNABASE OS</h3>
        Junior Astronaut Mission Trainer<br>
        Educational Space Engineering Simulation<br>
        NASA DONKI & NASA APOD Data Sources
    </div>
    """,
    unsafe_allow_html=True
)
