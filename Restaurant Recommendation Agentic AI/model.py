from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI   # If using OpenAI
# from langchain_community.llms import HuggingFaceHub   # If using HuggingFace SLM

# Dummy restaurant dataset
restaurants = [
    {"name": "Sushi Zen", "cuisine": "Japanese", "price": "high", "location": "Downtown"},
    {"name": "Curry House", "cuisine": "Indian", "price": "medium", "location": "Uptown"},
    {"name": "Pasta Bella", "cuisine": "Italian", "price": "medium", "location": "Midtown"},
    {"name": "Taco Fiesta", "cuisine": "Mexican", "price": "low", "location": "Downtown"},
    {"name": "Green Garden", "cuisine": "Vegan", "price": "medium", "location": "Suburb"},
]

# Convert dataset into text form for the model
restaurant_text = "\n".join(
    [f"{r['name']} - {r['cuisine']} - {r['price']} price - {r['location']}" for r in restaurants]
)

# ---- Choose your LLM ----
# OpenAI (small LLMs like gpt-3.5-turbo can be considered SLMs in practice)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# OR HuggingFace local model (if you prefer fully offline small model)
# llm = HuggingFaceHub(repo_id="google/flan-t5-small", model_kwargs={"temperature":0.7, "max_length":512})

# ---- Create LangChain Prompt ----
prompt = PromptTemplate(
    input_variables=["preferences", "restaurant_data"],
    template="""
You are a restaurant recommendation assistant.
Here is the list of available restaurants:
{restaurant_data}

The user preferences are: {preferences}

Based on this, recommend the top 3 restaurants and explain briefly why.
    """
)

# ---- Build the LLM Chain ----
chain = LLMChain(llm=llm, prompt=prompt)

# ---- Example user preference ----
user_pref = "I want affordable Mexican or Indian food near Downtown."

# ---- Get recommendations ----
recommendation = chain.run({"preferences": user_pref, "restaurant_data": restaurant_text})

print("🍽️ Restaurant Recommendations:")
print(recommendation)
