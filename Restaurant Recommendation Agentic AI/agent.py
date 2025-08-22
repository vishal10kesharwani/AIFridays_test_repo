from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load small language model from HuggingFace
llm = HuggingFaceHub(repo_id="google/flan-t5-small", model_kwargs={"temperature": 0.5})

# Prompt template
prompt = PromptTemplate(
    input_variables=["location", "cuisine"],
    template="""
You are a restaurant recommendation assistant.

User location: {location}
Cuisine preference: {cuisine}

Suggest 3 restaurants in the area that serve this cuisine. For each, include:
- Restaurant name
- 2 popular dishes
"""
)

# Chain setup
chain = LLMChain(llm=llm, prompt=prompt)

# Function to get recommendations
def get_recommendations(location, cuisine):
    return chain.run(location=location, cuisine=cuisine)