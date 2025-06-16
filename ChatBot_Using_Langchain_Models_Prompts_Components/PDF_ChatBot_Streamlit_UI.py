import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import fitz  # PyMuPDF
import tempfile

# Extract text from PDF
def extract_pdf_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Streamlit UI setup
st.set_page_config(page_title="PDF Viva Chatbot (Ollama)", layout="wide")
st.title("📘 PDF Viva Examiner - Powered by Ollama")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    with st.spinner("Extracting PDF content..."):
        pdf_text = extract_pdf_text(uploaded_file)
        pdf_text = pdf_text[:5000]  # Truncate to fit model context

    # Initialize Ollama model (e.g., llama3, mistral, codellama)
    model = ChatOllama(model="qwen2.5:0.5b")  # Change to your model if needed

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            SystemMessage(content=f"""You are an expert examiner conducting a viva based on the contents of the following PDF content:

--- START OF PDF CONTENT ---
{pdf_text}
--- END OF PDF CONTENT ---

Ask me questions directly based on this content. After I respond, evaluate my answer strictly with reference to the PDF. Explain if wrong. Do not reveal answers unless I try. Be professional, like a real viva.""")
        ]

    st.subheader("🗣️ Viva Chat Interface")

    user_input = st.chat_input("Type your response or question...")

    if user_input:
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        with st.spinner("AI is thinking..."):
            response = model.invoke(st.session_state.chat_history)
            st.session_state.chat_history.append(AIMessage(content=response.content))

    # Render chat messages
    for msg in st.session_state.chat_history:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)
