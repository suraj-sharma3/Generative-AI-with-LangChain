'''
Streamlit Viva Application

Project Description:
This project implements a Streamlit-based application that conducts a viva (oral exam) for students on any book provided as a PDF. The student enters their name, grade, subject, and uploads the PDF of the book. Upon clicking "Start Viva", the application extracts all text from the PDF, feeds it to a LangChain-based ChatOpenAI model for question generation and evaluation, and dynamically generates questions. Each question is presented in text and audio (via TTS). The student records their spoken answer, which is converted to text using speech recognition. The model evaluates the answer for correctness, adapts difficulty based on performance and detected learning disorders, and provides feedback. All interactions—questions asked, correctness, timings, scores, and detected learning disorders—are logged to a CSV file. At the end of the viva, the student's performance stats (excluding learning disorder) are displayed and saved.
''' 
import streamlit as st
import fitz  
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from gtts import gTTS
import tempfile
import time
import pandas as pd
import speech_recognition as sr
import os

# ------------------ Configuration ------------------
load_dotenv()  # load OPENAI_API_KEY from .env
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ------------------ Helper Functions ------------------

def extract_pdf_text(pdf_file):
    """
    Extract all text from the uploaded PDF using PyMuPDF.
    `pdf_file` is the Streamlit UploadedFile, which has a .read() method.
    """
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def generate_question(context, difficulty):
    """Generate a question via LangChain ChatOpenAI based on context and difficulty."""
    prompt = (
        f"You are an examiner. Given the following content, generate one question at difficulty level '{difficulty}':\n{context}"
    )
    result = model.invoke(prompt)
    return result.content.strip()


def text_to_speech(text):
    """Convert text to speech and return path to audio file."""
    tts = gTTS(text=text)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name


def recognize_speech(audio_path):
    """Convert recorded WAV audio file to text using SpeechRecognition."""
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return ""


def evaluate_answer(context, question, answer):
    """Evaluate student's answer via LangChain ChatOpenAI and adjust difficulty/disorders."""
    prompt = (
        f"Context: {context}\nQuestion: {question}\nStudent's Answer: {answer}\n"
        "Assess if the answer is correct. Provide feedback. "
        "Also estimate student's preparation level to adjust difficulty (easy, medium, hard). "
        "After 10 answers, if a learning disorder is detected, name it, otherwise reply None."
    )
    result = model.invoke(prompt)
    lines = result.content.strip().split("\n")
    is_correct = 'correct' in lines[0].lower()
    feedback = lines[1] if len(lines) > 1 else ''
    new_difficulty = lines[2].split()[-1].lower() if len(lines) > 2 else 'medium'
    potential_disorder = None if len(lines) < 4 or lines[3].lower() == 'none' else lines[3]
    return is_correct, feedback, new_difficulty, potential_disorder


def save_results(data, filename="viva_results.csv"):
    """Append session results to CSV file."""
    df = pd.DataFrame([data])
    header = not os.path.exists(filename)
    df.to_csv(filename, mode='a', index=False, header=header)

# ------------------ Streamlit App ------------------

def main():
    st.title("📚 PDF-Based Viva App")

    # --- User Details Input ---
    name = st.text_input("Name:")
    grade = st.text_input("Grade:")
    subject = st.text_input("Subject:")
    book = st.text_input("Book Title:")
    pdf_file = st.file_uploader("Upload Book PDF:", type=["pdf"] )

    if 'started' not in st.session_state:
        st.session_state.started = False
        st.session_state.stats = []
        st.session_state.difficulty = 'medium'
        st.session_state.disorder = None
        st.session_state.count = 0
        st.session_state.correct = 0
        st.session_state.incorrect = 0

    if st.button("Start Viva") and pdf_file and name and grade and subject and book:
        st.session_state.started = True
        st.session_state.context = extract_pdf_text(pdf_file)
        st.session_state.start_time = time.time()
        st.success("Viva Started!")

    if st.session_state.started:
        # Generate question
        q = generate_question(st.session_state.context, st.session_state.difficulty)
        st.markdown(f"**Question:** {q}")
        audio_path = text_to_speech(q)
        st.audio(audio_path)

        # Record answer
        audio_bytes = st.audio_input("Record your answer", format="wav")
        if audio_bytes:
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_wav.write(audio_bytes)
            temp_wav.close()

            ans_text = recognize_speech(temp_wav.name)
            st.write(f"Your Answer: {ans_text}")

            # Evaluate
            start_ans = time.time()
            correct, feedback, new_diff, disorder = evaluate_answer(
                st.session_state.context, q, ans_text
            )
            elapsed = time.time() - start_ans

            # Update stats
            st.session_state.count += 1
            if correct:
                st.session_state.correct += 1
                st.success("Correct! " + feedback)
            else:
                st.session_state.incorrect += 1
                st.error("Incorrect! " + feedback)

            # Adjust difficulty & disorder
            st.session_state.difficulty = new_diff
            if st.session_state.count >= 10 and not st.session_state.disorder:
                st.session_state.disorder = disorder

            # Log interaction
            st.session_state.stats.append({
                'question': q,
                'answer': ans_text,
                'correct': correct,
                'feedback': feedback,
                'time_taken': round(elapsed, 2)
            })

            if st.button("Stop Viva"):
                data = {
                    'name': name,
                    'grade': grade,
                    'subject': subject,
                    'book': book,
                    'questions_asked': st.session_state.count,
                    'correct': st.session_state.correct,
                    'incorrect': st.session_state.incorrect,
                    'score': f"{st.session_state.correct}/{st.session_state.count}",
                    'times': [s['time_taken'] for s in st.session_state.stats],
                    'learning_disorder': st.session_state.disorder
                }
                save_results(data)
                st.write("## Viva Summary")
                st.write(f"Questions Asked: {data['questions_asked']}")
                st.write(f"Correct: {data['correct']}")
                st.write(f"Incorrect: {data['incorrect']}")
                st.write(f"Score: {data['score']}")
                st.write(f"Time per Question: {data['times']}")
                st.session_state.started = False

if __name__ == '__main__':
    main()
