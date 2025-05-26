from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1", # Put the name of the model from hugging face you want to use here
    task="text-generation" # Put the task that the model performs from hugging face here
)

model = ChatHuggingFace(llm=llm)

result = model.invoke("Explain recurrent neural networks")

print(result.content)