import streamlit as st
import fitz

uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")

print(type(uploaded_pdf))

# Extract text from PDF
def extract_pdf_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="None")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

pdf_text = extract_pdf_text(uploaded_pdf)

print(pdf_text)


