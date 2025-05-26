from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # load the environment variables

llm = OpenAI(model = "gpt-3.5-turbo-instruct")

result = llm.invoke("What are scales and chords in music?") # provide prompt to invoke method

print(result)