from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model = "gpt-4", temperature=0, max_tokens=100)

result = model.invoke("What is the difference between a note and melody in music?")

print(result.content)