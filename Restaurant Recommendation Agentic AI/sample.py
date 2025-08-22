# app.py
import os
import math
import json
import requests
import httpx
import streamlit as st
from streamlit_javascript import st_javascript
import folium
from streamlit_folium import st_folium

# LangChain / Vector Store
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

import requests
requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.verify = False
requests.get = session.get

# ---------- CONFIG / KEYS ----------
# Set these as environment variables for safety:
#   MAPBOX_TOKEN=your_mapbox_public_token
#   GENAI_API_KEY=your_api_key  (for your GenAI Lab/OpenAI-compatible endpoint)
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "pk.eyJ1IjoiZGV2LXZpc2hhbCIsImEiOiJjbG91MWUxbGIwZmtrMmlxZXlzbDJpcmJ4In0.znHtQ6XI6lpj8VqREEmCGw")
GENAI_API_KEY = os.getenv("GENAI_API_KEY", "sk-h4SzToxOqOneSAXq191PXA")

# Enterprise environments sometimes need a cache dir for tiktoken
os.environ.setdefault("TIKTOKEN_CACHE_DIR", "./token")

# NOTE: If you are behind a corporate proxy with SSL interception,
# and you see SSL errors, you can (TEMPORARILY) set:
# os.environ["REQUESTS_CA_BUNDLE"] = r"C:\path\to\your\corporate\ca-bundle.pem"

# ---------- STREAMLIT PAGE ----------
st.set_page_config(page_title="🍽️ AI-Powered Restaurant Recommendation", layout="wide")
st.title("🍽️ AI-Powered Restaurant Recommendation")

with st.expander("🔑 Configure API Keys (stored only for this session)"):
    _mapbox_in = st.text_input("Mapbox Access Token", value=MAPBOX_TOKEN, type="password")
    _genai_in = st.text_input("GenAI/OpenAI-Compatible API Key", value=GENAI_API_KEY, type="password")
    if _mapbox_in:
        MAPBOX_TOKEN = _mapbox_in
    if _genai_in:
        GENAI_API_KEY = _genai_in

# Basic validation
if not MAPBOX_TOKEN:
    st.error("Mapbox token missing. Please provide MAPBOX_TOKEN.")
if not GENAI_API_KEY:
    st.warning("GenAI API key missing. Recommendations may fail until provided.")

# ---------- LLM & EMBEDDINGS ----------
# Your enterprise-compatible base URL + models
GENAI_BASE_URL = "https://genailab.tcs.in"

# httpx client (optionally disable SSL verification in tough corp networks)
client = httpx.Client(verify=True)  # set to False only if you must

llm = ChatOpenAI(
    base_url=GENAI_BASE_URL,
    model="azure_ai/genailab-maas-DeepSeek-V3-0324",
    api_key=GENAI_API_KEY,
    http_client=client,
    temperature=0.2,
)

embeddings = OpenAIEmbeddings(
    base_url=GENAI_BASE_URL,
    model="azure/genailab-maas-text-embedding-3-large",
    api_key=GENAI_API_KEY,
    http_client=client,
)

# 📍 Get Device Location with Permission Handling
coords = st_javascript("""
    await new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve(null); return;
      }

      navigator.permissions.query({ name: "geolocation" }).then(function(result) {
        if (result.state === "granted" || result.state === "prompt") {
          navigator.geolocation.getCurrentPosition(
            (pos) => resolve([pos.coords.latitude, pos.coords.longitude]),
            (err) => resolve(null),
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
          );
        } else {
          resolve(null);
        }
      });
    });
""")

if coords:
    lat, lon = coords
else:
    st.warning("⚠️ Location not granted. Using fallback: Mumbai, India")
    lat, lon = 19.0760, 72.8777  # Fallback to Mumbai

# 🏠 Reverse Geocoding (Coordinates ➝ Location Name)
def get_location_name(lat, lon):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json"
    params = {
        "access_token": MAPBOX_TOKEN,
        "types": "place,locality,neighborhood,address"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "features" in data and len(data["features"]) > 0:
        return data["features"][0]["place_name"]
    return "Unknown Location"

user_location_name = get_location_name(lat, lon)

# 🍴 Fetch Nearby Restaurants (within 10km)
def get_nearby_restaurants(lat, lon, query="restaurant"):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    params = {
        "proximity": f"{lon},{lat}",
        "limit": 5,
        "access_token": MAPBOX_TOKEN
    }
    response = requests.get(url, params=params)
    return response.json()

restaurant_data = get_nearby_restaurants(lat, lon)

# 🎯 Display User Location + Restaurants in One Div
st.subheader("📍 Your Location & Nearby Restaurants")
with st.container():
    st.markdown(f"**You are here:** {user_location_name} ({lat:.4f}, {lon:.4f})")

    if "features" in restaurant_data:
        st.markdown("### 🍴 Top Nearby Restaurants")
        for place in restaurant_data["features"]:
            st.write(f"- {place['text']} ({place['place_name']})")
    else:
        st.warning("No restaurants found nearby.")


col_a, col_b = st.columns(2)
with col_a:
    default_lat = 19.0760
    user_lat = st.number_input("Latitude", value=float(coords[0]) if coords else default_lat, format="%.6f")
with col_b:
    default_lon = 72.8777
    user_lon = st.number_input("Longitude", value=float(coords[1]) if coords else default_lon, format="%.6f")

st.caption("Tip: If geolocation was blocked or failed, adjust lat/lon above.")

# ---------- REVERSE GEOCODING TO GET ENGLISH LOCATION NAME ---------- # NEW
rev_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{user_lon},{user_lat}.json"
rev_params = {"access_token": MAPBOX_TOKEN, "language": "en"}
rev_res = requests.get(rev_url, params=rev_params).json()
user_location_name = rev_res.get("features", [{}])[0].get("place_name", "Unknown location")

# ---------- SHOW LOCATION + RAW MAPBOX OUTPUT IN ONE DIV ---------- # NEW
with st.container():
    st.markdown("### 🌍 Detected Location Info")
    st.write(f"**Location (English):** {user_location_name}")
    st.json(rev_res)  # pretty-print the full Mapbox response

# ---------- GEOLOCATION ----------
st.subheader("📍 Your Location")
coords = st_javascript("""
    await new Promise((resolve) => {
      if (!navigator.geolocation) { resolve(null); return; }
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve([pos.coords.latitude, pos.coords.longitude]),
        () => resolve(null),
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    });
""")

col_a, col_b = st.columns(2)
with col_a:
    default_lat = 19.0760
    user_lat = st.number_input("Latitude", value=float(coords[0]) if coords else default_lat, format="%.6f")
with col_b:
    default_lon = 72.8777
    user_lon = st.number_input("Longitude", value=float(coords[1]) if coords else default_lon, format="%.6f")

st.caption("Tip: If geolocation was blocked or failed, adjust lat/lon above.")

# ---------- USER PREFERENCES ----------
st.subheader("🤝 Your Preferences")
pref_cuisine = st.text_input("Cuisine / preference (e.g., Italian, Vegan, spicy, seafood, budget-friendly)", "")
min_rating = st.slider("Minimum rating", 3.0, 5.0, 4.0, 0.1)
search_radius_km = st.slider("Search radius (km)", 1, 20, 10)

# ---------- MAPBOX: FETCH NEARBY RESTAURANTS ----------
def haversine_m(user_lat, user_lon, lat2, lon2):
    R = 6371000.0
    phi1 = math.radians(user_lat)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - user_lat)
    dlmb = math.radians(lon2 - user_lon)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlmb/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_nearby_restaurants(lat, lon, radius_m=10000, limit=50):
    """
    Uses Mapbox Geocoding API for 'restaurant' POIs, biases by proximity,
    then filters by actual distance (≤ radius_m).
    Note: Mapbox Geocoding doesn't return ratings; we generate demo ratings.
    """
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/restaurant.json"
    params = {
        "proximity": f"{lon},{lat}",
        "types": "poi",
        "limit": limit,
        "language": "en",
        "access_token": MAPBOX_TOKEN
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.SSLError as e:
        st.error("SSL certificate error contacting Mapbox. If you're on corporate network, set REQUESTS_CA_BUNDLE to your corporate CA.")
        raise e
    except requests.RequestException as e:
        st.error(f"Mapbox request failed: {e}")
        raise e

    features = resp.json().get("features", [])
    out = []
    for f in features:
        coords = f.get("geometry", {}).get("coordinates", [])
        if len(coords) != 2:
            continue
        lon2, lat2 = coords
        dist_m = haversine_m(lat, lon, lat2, lon2)
        if dist_m <= radius_m:
            # Demo rating: since Mapbox doesn't provide ratings, we synthesize 3.0–5.0
            pseudo_rating = round(3.0 + (hash(f.get("text", "")) % 21) / 10.0, 1)  # 3.0 to 5.0 in 0.1 steps
            category = (f.get("properties", {}) or {}).get("category", "Restaurant")
            out.append({
                "name": f.get("text", "Unknown"),
                "full_address": f.get("place_name", ""),
                "lat": lat2,
                "lon": lon2,
                "distance_m": int(dist_m),
                "category": category,
                "rating": pseudo_rating
            })
    # Sort by distance, then rating desc for display convenience
    out.sort(key=lambda r: (r["distance_m"], -r["rating"]))
    return out

radius_m = int(search_radius_km * 1000)
restaurants = get_nearby_restaurants(user_lat, user_lon, radius_m=radius_m, limit=50)

st.write(f"Found **{len(restaurants)}** restaurants within **{search_radius_km} km**.")

# ---------- DISPLAY MAP ----------
map_col, list_col = st.columns([3, 2])
with map_col:
    if MAPBOX_TOKEN and restaurants:
        tiles_url = f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_TOKEN}"
        m = folium.Map(location=[user_lat, user_lon], zoom_start=13, tiles=tiles_url, attr="Mapbox")
        folium.Marker([user_lat, user_lon], tooltip="You are here", icon=folium.Icon(color="blue")).add_to(m)
        for r in restaurants:
            folium.Marker(
                [r["lat"], r["lon"]],
                tooltip=f"{r['name']} ({r['rating']}⭐, {r['distance_m']//1000}km)",
                popup=f"{r['full_address']}"
            ).add_to(m)
        st_folium(m, height=500, width=None)

with list_col:
    st.subheader("Nearby Restaurants")
    for r in restaurants[:10]:
        st.write(f"**{r['name']}** — {r['rating']}⭐ — {r['distance_m']//1000}.{(r['distance_m']%1000)//100} km")
        st.caption(r["full_address"])
        st.progress(min(1.0, (r["rating"] - 3.0) / 2.0))  # simple visual rating bar

# ---------- BUILD DOCS FOR RAG ----------
def build_docs(rests):
    docs = []
    for r in rests:
        docs.append(
            f"Restaurant: {r['name']}\n"
            f"Category: {r['category']}\n"
            f"Rating: {r['rating']}\n"
            f"DistanceMeters: {r['distance_m']}\n"
            f"Address: {r['full_address']}\n"
            f"Coordinates: ({r['lat']},{r['lon']})\n"
        )
    return docs

docs = build_docs(restaurants)
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
chunks = []
for d in docs:
    chunks.extend(splitter.split_text(d))

# Recreate vectorstore each run (for simplicity). For persistence, set a persist_directory.
if chunks:
    vectorstore = Chroma.from_texts(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
else:
    vectorstore = None
    retriever = None

# ---------- CUSTOM PROMPT FOR RECOMMENDATIONS ----------
prompt_tmpl = PromptTemplate.from_template(
    """You are a helpful restaurant recommender.
User preference: {preference}
Minimum rating: {min_rating}

From the provided retrieved context, choose up to 5 restaurants that best match the user's preference,
prioritizing higher ratings and closer distance. Respond in concise bullet points:
- Name — Rating⭐ — Distance (km) — Category
- One short reason aligned with the preference
If nothing matches, say so.

Context:
{context}
"""
)

# We’ll manually retrieve context and then call LLM with a single prompt:
st.subheader("✨ Get Recommendations")
if retriever:
    user_pref_text = pref_cuisine.strip() if pref_cuisine else "General good options"
    # Gather top docs (strings)
    retrieved = retriever.get_relevant_documents(user_pref_text or "restaurant")
    context_text = "\n---\n".join([d.page_content for d in retrieved]) if retrieved else "No context."

    if st.button("Recommend for me"):
        prompt = prompt_tmpl.format(
            preference=user_pref_text,
            min_rating=min_rating,
            context=context_text
        )
        # Final guardrail: tell model about rating threshold in the prompt
        response = llm.invoke(prompt)
        st.markdown("#### 🍴 Recommendations")
        st.write(response.content)
else:
    st.info("No restaurants found to build recommendations. Try increasing radius or check your Mapbox token.")
