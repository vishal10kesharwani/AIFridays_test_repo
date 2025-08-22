import os
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()
GENAI_BASE_URL = os.getenv("GENAI_BASE_URL")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

client = httpx.Client(verify=False)

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

prompt = PromptTemplate(
    input_variables=["event_type", "date", "guests", "venue_type", "theme", "location", "food", "budget"],
    template="""
    You are an Event Planning Assistant.
    Plan a {event_type} event on {date} for {guests} guests.
    Venue type: {venue_type}, Theme: {theme}, Location: {location}.
    Food preferences: {food}, Budget: {budget}.
    Provide a structured plan including venue, decoration, food, and overall experience.
    """
)

def plan_event(inputs):
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(inputs)
