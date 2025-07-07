import streamlit as st
import fitz  # PyMuPDF
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
model = ChatGroq(
    temperature=0,
    groq_api_key=groq_api_key,
    model_name="meta-llama/llama-guard-4-12b"  # or "gemma2-9b-it" if available
)

st.title("EvaluMate: AI-Powered Viva Bot")

# Initialize session states
for key in [
    "pdf_text_dict", "questions_dict", "current_question_index", 
    "user_answers", "scores", "final_score", "viva_status"
]:
    if key not in st.session_state:
        st.session_state[key] = {} if "dict" in key else 0 if "index" in key else [] if key == "scores" else "stopped"

# Input Fields
name = st.text_input("Name : ")
grade = st.text_input("Grade : ")
subject = st.text_input("Subject : ")
book_title = st.text_input("Book Title : ")

# PDF Upload
st.header("Upload a Book's PDF File")
book_pdf_file = st.file_uploader("Choose a Book's PDF file", type="pdf")

# Extract Text from PDF
if book_pdf_file is not None and not st.session_state.pdf_text_dict:
    pdf_bytes = book_pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            st.session_state.pdf_text_dict[i + 1] = text

    full_text = "\n".join(st.session_state.pdf_text_dict.values())[:8000]  # Truncate to fit token limits

    # Send to LLM to generate questions
    with st.spinner("Generating questions using LLM..."):
        system_prompt = (
            "You are an examiner. Given the book content, generate 15 question-answer pairs: "
            "5 easy, 5 moderate, and 5 difficult. Respond with JSON like this: \n"
            "{\"easy\": [{\"question\": \"...\", \"answer\": \"...\"}], \"moderate\": [...], \"difficult\": [...]}"
        )
        
        prompt_str = system_prompt + "\n\n" + full_text
        response = model.invoke([
            SystemMessage(content="You are an examiner."),
            HumanMessage(content=prompt_str)
        ])

        st.session_state.questions_dict = json.loads(response.content)
        st.session_state.viva_status = "ready"
        st.success("Questions generated. Click Start to begin viva.")

# --- Viva Logic ---
def get_all_questions():
    all_qs = []
    for level in ["easy", "moderate", "difficult"]:
        all_qs.extend(st.session_state.questions_dict.get(level, []))
    return all_qs

# Start/Stop Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Viva"):
        st.session_state.viva_status = "started"
        st.session_state.current_question_index = 0
        st.session_state.scores = []
        st.session_state.user_answers = []
with col2:
    if st.button("Stop Viva"):
        st.session_state.viva_status = "stopped"
        st.info("Viva stopped.")

# Display question, get answer, evaluate
if st.session_state.viva_status == "started":
    all_questions = get_all_questions()
    if st.session_state.current_question_index < len(all_questions):
        current_q = all_questions[st.session_state.current_question_index]
        st.subheader(f"Question {st.session_state.current_question_index + 1}:")
        st.markdown(current_q["question"])

        user_answer = st.text_area("Your Answer:", key=f"ans_{st.session_state.current_question_index}")
        if st.button("Submit Answer"):
            correct_ans = current_q["answer"]
            eval_prompt = (
                f"Evaluate the user's answer to the following question:\n"
                f"Question: {current_q['question']}\n"
                f"Correct Answer: {correct_ans}\n"
                f"User Answer: {user_answer}\n"
                f"Give feedback and score out of 10 as JSON: {{\"feedback\": \"...\", \"score\": int}}"
            )
            response = model.invoke([HumanMessage(content=eval_prompt)])
            try:
                eval_result = json.loads(response.content)
                st.session_state.scores.append(eval_result["score"])
                st.session_state.user_answers.append({
                    "question": current_q["question"],
                    "user_answer": user_answer,
                    "correct_answer": correct_ans,
                    "feedback": eval_result["feedback"],
                    "score": eval_result["score"]
                })
                st.success(f"Score: {eval_result['score']}/10")
                st.info(f"Feedback: {eval_result['feedback']}")
                st.session_state.current_question_index += 1
            except Exception as e:
                st.error("Failed to parse feedback. Try again.")
    else:
        st.session_state.viva_status = "done"

# Final Score
if st.session_state.viva_status == "done":
    total = sum(st.session_state.scores)
    st.session_state.final_score = total
    st.success(f"🎓 Viva Completed! Final Score: {total} / 150")

    # Optionally show detailed results
    with st.expander("See Detailed Feedback"):
        for idx, ans in enumerate(st.session_state.user_answers):
            st.markdown(f"**Q{idx+1}:** {ans['question']}")
            st.markdown(f"**Your Answer:** {ans['user_answer']}")
            st.markdown(f"**Correct Answer:** {ans['correct_answer']}")
            st.markdown(f"**Feedback:** {ans['feedback']}")
            st.markdown(f"**Score:** {ans['score']} / 10")
            st.markdown("---")
