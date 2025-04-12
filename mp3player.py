import streamlit as st
from pygame import mixer
import tempfile

# Initialize pygame mixer
mixer.init()

st.title("🔊 Simple MP3 Player")
st.write("Upload an MP3 file and play it!")

# Upload MP3 file
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

if uploaded_file:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    # Play button
    if st.button("Play"):
        mixer.music.load(tmp_file_path)
        mixer.music.play()
        st.success("Playing...")

    # Stop button
    if st.button("Stop"):
        mixer.music.stop()
        st.info("Playback stopped.")
else:
    st.warning("Please upload an MP3 file first.")