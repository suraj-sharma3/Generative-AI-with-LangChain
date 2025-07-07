import streamlit as st
from streamlit_mic_recorder import speech_to_text

st.title("🎤 Speech-to-Text with Streamlit")

st.write("Click the button and speak—when you stop, your speech will be transcribed and displayed below.")

# Record and transcribe once per click
text = speech_to_text(
    language="en",
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    just_once=True,
    use_container_width=True,
    key="stt"
)

if text:
    st.subheader("📝 You said:")
    st.write(text)




