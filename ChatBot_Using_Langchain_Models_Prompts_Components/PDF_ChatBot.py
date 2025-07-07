from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import fitz  # PyMuPDF

def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

load_dotenv()

# Load your PDF
pdf_path = r"C:\Users\OMOLP094\Desktop\My_GitHub_Repos\Generative-AI-with-LangChain\ChatBot_Using_Langchain_Models_Prompts_Components\machine_learning_tutorial.pdf"  # <-- Replace with your actual PDF path
pdf_text = extract_pdf_text(pdf_path)

# Truncate if too large for context (especially important for hosted models)
pdf_text = pdf_text[:5000]  # You can increase this based on model token limit

# Create the model endpoint
model = ChatOpenAI(model = "o4-mini", temperature=0, max_tokens=100)

# System message with PDF content embedded
chat_history = [
    SystemMessage(content=f"""You are an expert examiner conducting a viva based on the contents of the following PDF content:

--- START OF PDF CONTENT ---
{pdf_text}
--- END OF PDF CONTENT ---

Ask me questions directly based on this content. After I respond, evaluate my answer strictly with reference to the PDF. Explain if wrong. Do not reveal answers unless I try. Be professional, like a real viva.""")
]

while True:
    user_input = input('You: ')
    chat_history.append(HumanMessage(content=user_input))
    if user_input.lower() == 'exit':
        break
    result = model.invoke(chat_history)
    chat_history.append(AIMessage(content=result.content))
    print("AI:", result.content)
