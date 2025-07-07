import streamlit as st
import fitz  # PyMuPDF
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os

# ------------------ Load API Key ------------------ #
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# ------------------ Initialize Model ------------------ #
model = ChatGroq(
    temperature=0,
    groq_api_key=groq_api_key,
    model_name="gemma2-9b-it"
)

# ------------------ App Title ------------------ #
st.title("EvaluMate Viva Bot")

# ------------------ Initialize Session State ------------------ #
if "pdf_text_dict" not in st.session_state:
    st.session_state.pdf_text_dict = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "awaiting_answer" not in st.session_state:
    st.session_state.awaiting_answer = False

if "viva_status" not in st.session_state:
    st.session_state.viva_status = "stopped"

# ------------------ User Details ------------------ #
st.sidebar.header("Student Information")
name = st.sidebar.text_input("Name : ")
grade = st.sidebar.text_input("Grade : ")
subject = st.sidebar.text_input("Subject : ")
book_title = st.sidebar.text_input("Book Title : ")

# ------------------ Upload PDF ------------------ #
st.header("📘 Upload Your Book PDF")
book_pdf_file = st.file_uploader("Choose a Book's PDF file", type="pdf")

if book_pdf_file is not None:
    pdf_bytes = book_pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    st.write(f"✅ PDF Uploaded | Total Pages: {len(doc)}")

    st.session_state.pdf_text_dict.clear()
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            st.session_state.pdf_text_dict[i + 1] = text

# ------------------ Display PDF Page Text ------------------ #
if st.session_state.pdf_text_dict:
    selected_page = st.selectbox(
        "Select a page to view extracted text:",
        options=sorted(st.session_state.pdf_text_dict.keys()),
        format_func=lambda x: f"Page {x}"
    )
    st.text_area("Page Content", st.session_state.pdf_text_dict[selected_page], height=300)
else:
    st.info("📄 Upload a PDF to extract and view its content.")

# ------------------ Viva Controls ------------------ #
st.subheader("🎤 Viva Controls")
col1, col2 = st.columns(2)

with col1:
    if st.button("Start Viva"):
        st.session_state.viva_status = "started"

with col2:
    if st.button("Stop Viva"):
        st.session_state.viva_status = "stopped"

st.info(f"Current Viva Status: **{st.session_state.viva_status.upper()}**")

# ------------------ Viva Interaction ------------------ #
if st.session_state.viva_status == "started" and st.session_state.pdf_text_dict:
    pdf_combined_text = "\n\n".join(st.session_state.pdf_text_dict.values())

    # Add system prompt once
    if not st.session_state.chat_history:
        system_prompt = f"""You are an expert examiner conducting a viva based on the contents of the following PDF content:

--- START OF PDF CONTENT ---
{pdf_combined_text}
--- END OF PDF CONTENT ---

Ask one question at a time directly based on this content. After each student answer, evaluate the response strictly referring to the text. Provide feedback. Continue this loop until the viva is manually stopped. Be strict and professional like a real viva examiner."""
        st.session_state.chat_history.append(SystemMessage(content=system_prompt))
        st.session_state.awaiting_answer = False  # Ready to ask first question

    # Step 1: Ask next question
    if not st.session_state.awaiting_answer:
        result = model.invoke(st.session_state.chat_history)
        st.session_state.chat_history.append(AIMessage(content=result.content))
        st.session_state.current_question = result.content
        st.session_state.awaiting_answer = True
        st.rerun()

    # Step 2: Show current question & accept answer
    if st.session_state.current_question:
        st.markdown(f"**AI Question:** {st.session_state.current_question}")
        user_answer = st.text_area("Your Answer", key="answer_box", value=st.session_state.get("answer_box", ""))

        if st.button("Submit Answer", key="submit_btn"):
            if user_answer.strip():
                # Add user's answer
                st.session_state.chat_history.append(HumanMessage(content=user_answer))

                # Get AI feedback
                feedback = model.invoke(st.session_state.chat_history)
                st.session_state.chat_history.append(AIMessage(content=feedback.content))

                # Show feedback
                st.success("✅ Feedback:")
                st.write(feedback.content)

                # Reset state for next question
                st.session_state.awaiting_answer = False
                st.session_state.current_question = None
                st.session_state.answer_box = ""  # Clear the input box
                st.rerun()

            else:
                st.warning("⚠️ Please enter your answer before submitting.")

elif st.session_state.viva_status == "started" and not st.session_state.pdf_text_dict:
    st.warning("⚠️ Please upload a PDF file to start the viva.")
