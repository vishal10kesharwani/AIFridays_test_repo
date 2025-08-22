import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import os
import httpx
import tiktoken


import requests
requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.verify = False
requests.get = session.get

# Cache dir for tokens
tiktoken_cache_dir = "./token"
os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir
client = httpx.Client(verify=False)

# LLM Setup
llm = ChatOpenAI(
    base_url="https://genailab.tcs.in",
    model="azure_ai/genailab-maas-DeepSeek-V3-0324",
    api_key="sk-h4SzToxOqOneSAXq191PXA",   # replace with valid key
    http_client=client
)

embedding_model = OpenAIEmbeddings(
    base_url="https://genailab.tcs.in",
    model="azure/genailab-maas-text-embedding-3-large",
    api_key="sk-h4SzToxOqOneSAXq191PXA",   # replace with valid key
    http_client=client
)

# Streamlit UI
st.set_page_config(page_title="Restaurant Recommender")
st.title("🍽️ AI-Powered Restaurant Recommendation")

# ---- Step 1: Sample Restaurant Data ----
sample_data = [
    {
        "name": "Pizza Palace",
        "cuisine": "Italian",
        "location": "Mumbai",
        "rating": 4.5,
        "desc": "Authentic Italian pizzas with wood-fired ovens and cozy ambiance."
    },
    {
        "name": "Curry House",
        "cuisine": "Indian",
        "location": "Delhi",
        "rating": 4.2,
        "desc": "Traditional North Indian curries, naan, and kebabs."
    },
    {
        "name": "Dragon Wok",
        "cuisine": "Chinese",
        "location": "Bangalore",
        "rating": 4.3,
        "desc": "Delicious noodles, dumplings, and Chinese stir fry with modern flavors."
    },
    {
        "name": "Green Leaf",
        "cuisine": "Vegan",
        "location": "Pune",
        "rating": 4.7,
        "desc": "Plant-based healthy meals with organic ingredients and smoothies."
    },
    {
        "name": "Ocean Catch",
        "cuisine": "Seafood",
        "location": "Chennai",
        "rating": 4.6,
        "desc": "Fresh seafood with South Indian spices and beachside dining."
    }
]

# ---- Step 2: Convert to text format ----
docs = []
for r in sample_data:
    content = f"Restaurant: {r['name']}\nCuisine: {r['cuisine']}\nLocation: {r['location']}\nRating: {r['rating']}\nDescription: {r['desc']}"
    docs.append(content)

# Split into chunks (not strictly needed here since docs are small)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = []
for d in docs:
    chunks.extend(splitter.split_text(d))

# ---- Step 3: Embedding + Vector Store ----
vectorstore = Chroma.from_texts(chunks, embedding_model)
retriever = vectorstore.as_retriever()

# ---- Step 4: RetrievalQA Chain ----
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever
)

# ---- Step 5: Query UI ----
query = st.text_input("What kind of restaurant are you looking for?")
if query:
    answer = qa_chain.run(query)
    st.subheader("🍴 Recommended Options:")
    st.write(answer)
