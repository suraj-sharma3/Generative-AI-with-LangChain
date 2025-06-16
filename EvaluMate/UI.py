import streamlit as st
import time

# --- Page config ---
st.set_page_config(page_title="Viva Chatbot for Students with Learning Disorders", layout="centered")

st.title("🎓 Viva Chatbot Interface")

# --- 1. Dropdown for learning disorder selection ---
st.subheader("Select the Learning Disorder")
learning_disorders = ["Dyslexia", "Dysgraphia", "ADHD"]
selected_disorder = st.selectbox("Choose a learning disorder:", learning_disorders)
st.session_state["selected_disorder"] = selected_disorder

# --- 2. Difficulty level selection (always visible) ---
st.subheader("🎯 Select Difficulty Level for Viva")
difficulty_levels = ["Easy", "Medium", "Difficult"]
selected_difficulty = st.selectbox("Choose question difficulty level:", difficulty_levels)
st.session_state["selected_difficulty"] = selected_difficulty

# --- 3. PDF Upload Section ---
st.subheader("📘 Upload Course Material")
st.markdown("**Upload the PDF of your book that you want the viva to be conducted on**")

uploaded_pdf = st.file_uploader("Upload your PDF here", type=["pdf"])

# Initialize state flag if not already present
if "pdf_uploaded" not in st.session_state:
    st.session_state["pdf_uploaded"] = False

# Show progress bar only if file is uploaded and not yet processed
if uploaded_pdf is not None and not st.session_state["pdf_uploaded"]:
    progress_text = "Uploading PDF. Please wait..."
    with st.spinner(progress_text):
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)
        st.success("PDF uploaded successfully!")

    # Store PDF data and mark as uploaded
    pdf_file_data = uploaded_pdf.read()
    st.session_state["pdf_data"] = pdf_file_data
    st.session_state["pdf_uploaded"] = True

# --- 4. Start / Stop Viva Buttons ---
st.subheader("🎤 Viva Controls")

col1, col2 = st.columns(2)

with col1:
    start_clicked = st.button("▶️ Start Viva")
    if start_clicked:
        st.session_state["viva_running"] = True
        st.success("Viva started!")

with col2:
    stop_clicked = st.button("⏹️ Stop Viva")
    if stop_clicked:
        st.session_state["viva_running"] = False
        st.warning("Viva stopped.")
