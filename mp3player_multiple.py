import streamlit as st
from pygame import mixer
import tempfile
import time

mixer.init()  # Initialize mixer

st.title("🎵 Sequential MP3 Player")
st.write("Upload multiple MP3 files - they'll play in order when you click Play")

# Upload multiple MP3s
uploaded_files = st.file_uploader("Choose MP3 files", 
                                type=["mp3"],
                                accept_multiple_files=True)

if uploaded_files:
    # Store files temporarily
    temp_files = []
    for i, uploaded_file in enumerate(uploaded_files):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(uploaded_file.read())
            temp_files.append(tmp.name)
        st.write(f"Loaded: {uploaded_file.name}")

    # Play button
    if st.button("Play All"):
        for i, file in enumerate(temp_files):
            st.write(f"Now playing: {uploaded_files[i].name}")
            mixer.music.load(file)
            mixer.music.play()
            
            # Wait while current file is playing
            while mixer.music.get_busy():
                time.sleep(0.1)
        
        st.success("Playback complete!")

    # Stop button
    if st.button("Stop"):
        mixer.music.stop()
        st.warning("Playback stopped")
else:
    st.info("Please upload some MP3 files first")