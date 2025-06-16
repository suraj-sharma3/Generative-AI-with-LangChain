from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1", # Put the name of the model from hugging face you want to use here
    task="text-generation" # Put the task that the model performs from hugging face here
)

model = ChatHuggingFace(llm=llm)

chat_history = [
    SystemMessage(content='You are an expert examiner conducting a viva based on the contents of a specific PDF document that I will provide. Your role is to ask me questions directly based on the material in that PDF. After I respond to each question, evaluate the accuracy, completeness, and correctness of my answer strictly with reference to the PDF content. If the answer is incorrect, explain why and provide the correct response. Ask follow-up questions if necessary. Do not reveal answers unless I have attempted them or asked for clarification. Maintain a professional, academic tone as in an actual viva examination.')
]

while True:
    user_input = input('You: ')
    chat_history.append(HumanMessage(content=user_input))
    if user_input == 'exit':
        break
    result = model.invoke(chat_history)
    chat_history.append(AIMessage(content=result.content))
    print("AI: ",result.content)

print(chat_history)