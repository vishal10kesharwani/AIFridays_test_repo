import streamlit as st
from backend import auth, database
from backend.location_utils import get_location_name
import geocoder

# Initialize DB
database.init_db()

st.set_page_config(page_title="Event Planning Assistant", layout="wide")

# Session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.title("Login / Signup")

    choice = st.radio("Choose an option", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Signup"):
            if auth.signup(username, password):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists.")

    if choice == "Login":
        if st.button("Login"):
            user_id = auth.login(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

else:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Plan Event"])

    if page == "Home":
        st.title("Welcome to Event Planning Assistant 🎉")

        # Fetch device location
        g = geocoder.ip("me")
        lat, lon = g.latlng
        location_name = get_location_name(lat, lon)

        st.info(f"📍 Your detected location: {location_name}")

    if page == "Plan Event":
        st.title("Plan Your Event")

        from backend.planner_agent import plan_event

        event_type = st.selectbox("Event Type", ["Wedding", "Conference", "Birthday"])
        date = st.date_input("Date")
        guests = st.number_input("Number of Guests", min_value=10, step=10)
        venue_type = st.selectbox("Venue Type", ["Banquet Hall", "Open Ground", "Hotel", "Resort"])
        theme = st.text_input("Theme / Preference")
        food = st.multiselect("Food Menu", ["Lunch", "Dinner", "Starters", "Veg", "Non-Veg"])
        budget = st.number_input("Budget", min_value=1000, step=500)

        if st.button("Generate Plan"):
            g = geocoder.ip("me")
            lat, lon = g.latlng
            location_name = get_location_name(lat, lon)

            plan = plan_event({
                "event_type": event_type,
                "date": str(date),
                "guests": guests,
                "venue_type": venue_type,
                "theme": theme,
                "location": location_name,
                "food": ", ".join(food),
                "budget": budget
            })

            st.subheader("🎯 Suggested Plan")
            st.write(plan)
