import streamlit as st
import fitz  # PyMuPDF
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    temperature=0,
    groq_api_key = groq_api_key,
    model_name = "gemma2-9b-it" 
)

st.title("EvaluMate Viva Bot")

# --- Initialize session state ---
if "pdf_text_dict" not in st.session_state:
    st.session_state.pdf_text_dict = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False

# --- Input Fields ---
name = st.text_input("Name : ")
grade = st.text_input("Grade : ")
subject = st.text_input("Subject : ")
book_title = st.text_input("Book Title : ")

# --- Upload PDF and Extract Text ---
st.header("Upload a Book's PDF File")
book_pdf_file = st.file_uploader("Choose a Book's PDF file", type="pdf")

if book_pdf_file is not None:
    pdf_bytes = book_pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    st.write(f"Total Pages: {len(doc)}")

    st.session_state.pdf_text_dict.clear()
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            st.session_state.pdf_text_dict[i + 1] = text

# --- Display extracted content per page ---
if st.session_state.pdf_text_dict:
    selected_page = st.selectbox("Select a page to view its extracted text:", options=sorted(st.session_state.pdf_text_dict.keys()), format_func=lambda x: f"Page {x}")
    st.subheader(f"Text from Page {selected_page}")
    st.text_area("Page Content", st.session_state.pdf_text_dict[selected_page], height=300)
else:
    st.info("📄 Upload a PDF to extract and view its content.")

# --- Viva Status ---
if "viva_status" not in st.session_state:
    st.session_state.viva_status = "stopped"

col1, col2 = st.columns(2)

with col1:
    if st.button("Start Viva"):
        st.session_state.viva_status = "started"

with col2:
    if st.button("Stop Viva"):
        st.session_state.viva_status = "stopped"

st.info(f"Current status: {st.session_state.viva_status}")

# --- Create the model ---
# model = ChatOpenAI(model="o4-mini", temperature=0, max_tokens=100)

# --- Start Viva Interaction ---
if st.session_state.viva_status == "started" and st.session_state.pdf_text_dict:
    pdf_combined_text = "\n\n".join(st.session_state.pdf_text_dict.values())

    if not st.session_state.chat_history:
        system_prompt = f"""You are an expert examiner conducting a viva based on the contents of the following PDF content:

--- START OF PDF CONTENT ---
{pdf_combined_text}
--- END OF PDF CONTENT ---

Ask me questions directly based on this content. After I respond, evaluate my answer strictly with reference to the PDF. Explain if wrong. Do not reveal answers unless I try. Be professional, like a real viva."""
        st.session_state.chat_history.append(SystemMessage(content=system_prompt))

    # Step 1: Ask the user a question if not already awaiting answer
    if not st.session_state.awaiting_answer:
        result = model.invoke(st.session_state.chat_history)
        st.session_state.chat_history.append(AIMessage(content=result.content))
        st.session_state.current_question = result.content
        st.session_state.awaiting_answer = True

    # Step 2: Display the question and let user answer
    if st.session_state.current_question:
        st.markdown(f"**AI Question:** {st.session_state.current_question}")
        user_answer = st.text_area("Your Answer", key="answer_box")

        if st.button("Submit Answer"):
            if user_answer.strip():
                st.session_state.chat_history.append(HumanMessage(content=user_answer))
                feedback = model.invoke(st.session_state.chat_history)
                st.session_state.chat_history.append(AIMessage(content=feedback.content))

                st.success("**Feedback:**")
                st.write(feedback.content)

                # Reset state for next question
                st.session_state.awaiting_answer = False
                st.session_state.current_question = None
            else:
                st.warning("Please enter an answer before submitting.")

elif st.session_state.viva_status == "started" and not st.session_state.pdf_text_dict:
    st.warning("Please upload a PDF file to start the viva.")
