import streamlit as st
from backend.location_utils import get_location_name
import geocoder

def home_page():
    st.title("🏡 Home - Event Planning Assistant")

    # Detect location using IP
    g = geocoder.ip("me")
    if g.ok:
        lat, lon = g.latlng
        location_name = get_location_name(lat, lon)
        st.success(f"📍 You are currently in: **{location_name}**")
    else:
        st.warning("⚠️ Unable to detect your location automatically.")

    st.markdown("### What would you like to do?")
    st.markdown("- 🎉 Plan a new event")
    st.markdown("- 🏢 Browse available venues")
    st.markdown("- 📅 View or manage your booked events")

if __name__ == "__main__":
    home_page()
