'''README.md'''
# PDF-Based Viva Application

## Overview
This Streamlit application conducts an interactive viva (oral exam) based on any PDF book uploaded by the student. It uses OpenAI’s chat model to generate questions and evaluate answers, adapting difficulty in real time and detecting potential learning disorders.

## Features
- **User Inputs:** Name, Grade, Subject, Book Title, PDF upload.
- **Question Generation:** Dynamic via OpenAI, with difficulty levels (easy, medium, hard).
- **TTS:** Questions are spoken using gTTS; audio and text displayed.
- **Speech Recognition:** Student records answers in-app; converted to text via SpeechRecognition.
- **Evaluation:** Answers assessed by OpenAI; feedback provided.
- **Adaptive Difficulty:** Adjusts based on performance; after 10 questions, detects learning disorders.
- **Logging:** All interactions saved to `viva_results.csv`.
- **Summary Display:** Shows total questions, correct/incorrect, score, and response times.

## Requirements
- Python 3.7+
- Streamlit
- PyPDF2
- openai
- gTTS
- SpeechRecognition
- streamlit-audio-recorder
- pandas

Install via:
```
pip install streamlit PyPDF2 openai gTTS SpeechRecognition streamlit-audio-recorder pandas
```

## Setup
1. **API Key:** Export OpenAI key:
   ```bash
   export OPENAI_API_KEY="your_key_here"
   ```
2. **Run App:**
   ```bash
   streamlit run streamlit_viva_app.py
   ```

## Usage
1. Enter your Name, Grade, Subject, and Book Title.
2. Upload the PDF of the book.
3. Click **Start Viva** to begin.
4. Listen and read each generated question.
5. Click to record your answer; click again to stop.
6. View feedback and continue until you click **Stop Viva**.
7. Review your summary metrics at the end.

## File Structure
- `streamlit_viva_app.py` – Main application code.
- `viva_results.csv` – Logs session results.

## Notes
- Ensure a stable internet connection for API calls.
- The detected learning disorder is stored privately in the CSV and not displayed to the user.