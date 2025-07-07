import streamlit as st
import fitz  # PyMuPDF
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import io
import pyttsx3
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr

# ------------------ Load API & Init Model ------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    temperature=0,
    groq_api_key=groq_api_key,
    model_name="llama3-70b-8192"
)

st.title("📘 EvaluMate - Viva Question Evaluator")

# ------------------ Session State ------------------
if "pdf_text_dict" not in st.session_state:
    st.session_state.pdf_text_dict = {}
if "qa_dict" not in st.session_state:
    st.session_state.qa_dict = {}
if "all_qas" not in st.session_state:
    st.session_state.all_qas = []
if "qa_index" not in st.session_state:
    st.session_state.qa_index = 0
if "used_q_indices" not in st.session_state:
    st.session_state.used_q_indices = []

# ------------------ Input Fields ------------------
name = st.text_input("Name : ")
grade = st.text_input("Grade : ")
subject = st.text_input("Subject : ")
book_title = st.text_input("Book Title : ")

# ------------------ PDF Upload ------------------
st.header("Upload the Book's PDF")
book_pdf_file = st.file_uploader("Choose a PDF", type="pdf")

if book_pdf_file is not None:
    doc = fitz.open(stream=book_pdf_file.read(), filetype="pdf")
    st.session_state.pdf_text_dict.clear()

    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            st.session_state.pdf_text_dict[i + 1] = text

    st.success("✅ PDF uploaded and text extracted.")

# ------------------ Page Viewer ------------------
if st.session_state.pdf_text_dict:
    selected_page = st.selectbox("View a Page:", list(st.session_state.pdf_text_dict.keys()))
    st.text_area("Extracted Text", st.session_state.pdf_text_dict[selected_page], height=300)

# ------------------ Question Generation ------------------
if st.button("🔍 Generate Viva Questions"):
    if st.session_state.pdf_text_dict:
        full_text = "\n\n".join(st.session_state.pdf_text_dict.values())

        prompt = f"""
You are an expert examiner. Based on the following content:

--- CONTENT START ---
{full_text}
--- CONTENT END ---

Generate 15 viva questions along with their answers:
- 5 Easy
- 5 Moderate
- 5 Difficult

Format exactly like this:

Easy:
Q1: ...
A1: ...
...

Moderate:
Q6: ...
A6: ...
...

Difficult:
Q11: ...
A11: ...
...
        """

        response = llm.invoke(prompt)
        raw_output = response.content.strip()

        sections = {"Easy": [], "Moderate": [], "Difficult": []}
        current_section = None

        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            if "Easy" in line:
                current_section = "Easy"
            elif "Moderate" in line:
                current_section = "Moderate"
            elif "Difficult" in line:
                current_section = "Difficult"
            elif current_section and (line.startswith("Q") or line.startswith("A")):
                sections[current_section].append(line)

        qa_dict = {}
        all_qas = []
        for level, lines in sections.items():
            for i in range(0, len(lines), 2):
                try:
                    q = lines[i].split(":", 1)[1].strip()
                    a = lines[i + 1].split(":", 1)[1].strip()
                    all_qas.append({
                        "level": level,
                        "question": q,
                        "answer": a,
                        "user_answer": "",
                        "score": None
                    })
                except:
                    continue
            qa_dict[level] = all_qas

        st.session_state.qa_dict = qa_dict
        st.session_state.all_qas = all_qas
        st.session_state.qa_index = 0
        st.session_state.used_q_indices = []
        st.success("✅ Viva questions generated.")

# ------------------ Answer Evaluation ------------------
def evaluate_answer(question, correct_answer, user_answer):
    eval_prompt = f"""
You are a strict examiner. Here is the question, the correct answer, and a student's answer.

Question: {question}

Correct Answer: {correct_answer}

Student's Answer: {user_answer}

Evaluate the student's answer strictly and give a score out of 10. Just reply with a number between 0 and 10. No explanation, no extra words.
"""
    result = llm.invoke(eval_prompt)
    try:
        score = int(result.content.strip())
        return max(0, min(10, score))
    except:
        return 0

# ------------------ Adaptive Question Selector ------------------
def get_next_question(score):
    if score < 4:
        level = "Easy"
    elif score < 7:
        level = "Moderate"
    else:
        level = "Difficult"

    for i, qa in enumerate(st.session_state.all_qas):
        if qa["level"] == level and i not in st.session_state.used_q_indices:
            st.session_state.qa_index = i
            return

# ------------------ Viva UI ------------------
if st.session_state.all_qas:
    st.subheader("🧠 Viva Questions")

    current = st.session_state.qa_index
    qa = st.session_state.all_qas[current]

    st.markdown(f"**Question {len(st.session_state.used_q_indices) + 1} of 15** ({qa['level']})")
    st.markdown(f"**Q:** {qa['question']}")

    # TTS using pyttsx3
    if st.button("🔊 Read Question Aloud"):
        try:
            engine = pyttsx3.init()
            engine.say(qa["question"])
            engine.runAndWait()
        except Exception as e:
            st.warning(f"TTS failed: {e}")

    # Audio recording and transcription
    record_seconds = st.slider("Select recording time (seconds):", 3, 15, 5)

    if st.button("🎙️ Record Your Answer"):
        try:
            st.info("Recording... Speak now!")
            fs = 44100
            audio = sd.rec(int(record_seconds * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            wav.write("temp.wav", fs, audio)

            # Transcribe
            recognizer = sr.Recognizer()
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

                st.session_state.all_qas[current]["user_answer"] = text
                st.success("✅ Transcription Successful")
                st.text_area("Your Answer (from audio)", value=text, key=f"audio_text_{current}")

        except Exception as e:
            st.error(f"❌ Error during recording/transcription: {e}")

    # Manual edit box
    manual_answer = st.text_area("Edit Your Answer", value=qa.get("user_answer", ""), key=f"user_answer_{current}")

    if st.button("✅ Submit Answer"):
        st.session_state.all_qas[current]["user_answer"] = manual_answer
        score = evaluate_answer(qa["question"], qa["answer"], manual_answer)
        st.session_state.all_qas[current]["score"] = score
        st.session_state.used_q_indices.append(current)
        st.success(f"✅ Answer saved and scored: {score}/10")

        if len(st.session_state.used_q_indices) < len(st.session_state.all_qas):
            get_next_question(score)
        else:
            st.info("✅ All questions completed.")

# ------------------ Save Report ------------------
def save_qa_to_text_file(name, grade, subject, book_title, all_qas):
    output = io.StringIO()
    output.write(f"Name: {name}\nGrade: {grade}\nSubject: {subject}\nBook Title: {book_title}\n\n")
    output.write("Structured Viva Questions, Answers, and Scores\n")
    output.write("=" * 70 + "\n\n")

    for i, qa in enumerate(all_qas, 1):
        output.write(f"[{i}] Difficulty: {qa['level']}\n")
        output.write(f"Q: {qa['question']}\n")
        output.write(f"LLM Answer: {qa['answer']}\n")
        output.write(f"User Answer: {qa['user_answer'] if qa['user_answer'] else '[Not answered]'}\n")
        output.write(f"Score: {qa['score'] if qa['score'] is not None else '[Not evaluated]'} / 10\n")
        output.write("-" * 70 + "\n")

    return output.getvalue()

if st.session_state.all_qas:
    st.subheader("📄 Download Q&A + Scores")

    if st.button("📥 Generate Report"):
        file_content = save_qa_to_text_file(name, grade, subject, book_title, st.session_state.all_qas)
        st.download_button(
            label="Download as Text File",
            data=file_content,
            file_name="viva_evaluation_report.txt",
            mime="text/plain"
        )
