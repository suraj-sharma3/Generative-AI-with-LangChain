import streamlit as st
import os
import tempfile
import speech_recognition as sr
import pyttsx3
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceHub

# ========== Core Chatbot Engine ========== #
class PDFChatEvaluator:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.loader = PyPDFLoader(pdf_path)
        self.docs = self.loader.load()
        self.vector_store = self._create_vectorstore()
        self.qa_chain = self._create_qa_chain()
        self.engine = pyttsx3.init()

    def _create_vectorstore(self):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.from_documents(self.docs, embeddings)

    def _create_qa_chain(self):
        llm = HuggingFaceHub(repo_id="google/flan-t5-large", model_kwargs={"temperature": 0.2, "max_length": 512})
        return RetrievalQA.from_chain_type(llm=llm, retriever=self.vector_store.as_retriever())

    def ask_question(self, question):
        response = self.qa_chain.run(question)
        self._speak(response)
        return response

    def evaluate_answer(self, question, user_answer):
        # Score the user answer using LLM (simplified version)
        prompt = f"Question: {question}\nUser's Answer: {user_answer}\nEvaluate this answer out of 10 and suggest improvements."
        evaluation = self.qa_chain.run(prompt)
        return evaluation

    def _speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError:
            return "Speech service unavailable."

# ========== Streamlit UI Logic ========== #
def main():
    st.title("📘 PDF-Based Quiz Chatbot")

    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    if "ready" not in st.session_state:
        st.session_state.ready = False
    if "question" not in st.session_state:
        st.session_state.question = ""

    pdf_file = st.file_uploader("Upload your PDF", type=["pdf"])

    if pdf_file is not None and not st.session_state.ready:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name

        st.session_state.chatbot = PDFChatEvaluator(tmp_path)
        st.session_state.ready = True
        st.success("PDF uploaded and processed successfully!")

        preparedness = st.radio("How prepared are you with the content of the PDF?", ["Well Prepared", "Moderately Prepared", "Not Prepared"])

        st.info("I will now start asking questions based on the PDF.")

    if st.session_state.ready:
        if st.button("Ask me a question"):
            st.session_state.question = st.session_state.chatbot.ask_question("Ask a quiz question from this document")
            st.chat_message("assistant").markdown(f"**Question:** {st.session_state.question}")

        if st.session_state.question:
            user_input = st.text_input("Type your answer here or use voice input below:")
            if st.button("🎤 Use Voice Input"):
                voice_input = st.session_state.chatbot.listen()
                st.write(f"You said: {voice_input}")
                user_input = voice_input

            if user_input:
                evaluation = st.session_state.chatbot.evaluate_answer(st.session_state.question, user_input)
                st.chat_message("assistant").markdown(f"**Evaluation:** {evaluation}")

if __name__ == '__main__':
    main()
