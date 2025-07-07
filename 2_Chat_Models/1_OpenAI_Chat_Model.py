from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

# api_key = os.getenv("OPENAI_API_KEY")

groq_api_key = os.getenv("GROQ_API_KEY")

# print(api_key)

# model = ChatOpenAI(model = "gpt-4", temperature=0, max_tokens=100, api_key = groq_api_key)

llm = ChatGroq(
    temperature=0,
    groq_api_key = groq_api_key,
    model_name = "llama-3.3-70b-versatile" 
)

result = llm.invoke("What is the difference between a note and melody in music?")

print(result.content)