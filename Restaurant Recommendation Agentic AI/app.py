import streamlit as st
from agent import get_recommendations
# import agent

# Page config
st.set_page_config(page_title="🍽️ Restaurant Recommender", page_icon="🍴", layout="centered")

# Sidebar inputs
st.sidebar.header("Your Preferences")
location = st.sidebar.text_input("📍 Location", "Nagpur")
cuisine = st.sidebar.text_input("🍜 Cuisine", "South Indian")

# Main title
st.title("🍴 Restaurant Recommendation Agent")
st.markdown("Get personalized restaurant suggestions based on your location and taste.")

# Button to trigger recommendation
if st.sidebar.button("🔍 Find Restaurants"):
    with st.spinner("Searching for delicious options..."):
        result = get_recommendations(location, cuisine)
        st.success("Here are your top picks:")
        for line in result.strip().split("\n"):
            if line.strip():
                st.markdown(f"✅ {line}")