import streamlit as st
import pygame
import tempfile
import os
from pydub import AudioSegment
import threading
import atexit

# Initialize pygame mixer
pygame.mixer.init()

st.title("🎧 MP3 Mixer")
st.write("Upload multiple MP3 files and play them simultaneously")

# Global variables for audio management
mixed_audio_path = None
temp_files = []
is_playing = False

def cleanup():
    """Clean up temporary files"""
    global temp_files, mixed_audio_path
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass
    if mixed_audio_path and os.path.exists(mixed_audio_path):
        try:
            os.unlink(mixed_audio_path)
        except Exception:
            pass
    temp_files = []
    mixed_audio_path = None

# Register cleanup
atexit.register(cleanup)

def play_audio():
    """Play the mixed audio"""
    global is_playing
    try:
        pygame.mixer.music.load(mixed_audio_path)
        pygame.mixer.music.play()
        is_playing = True
        while pygame.mixer.music.get_busy() and is_playing:
            pygame.time.Clock().tick(10)
    except Exception as e:
        st.error(f"Playback error: {e}")
    finally:
        is_playing = False

# Upload multiple MP3s
uploaded_files = st.file_uploader("Choose MP3 files to mix", 
                                 type=["mp3"],
                                 accept_multiple_files=True)

if uploaded_files:
    # Display uploaded files
    st.write("Files to mix:")
    for file in uploaded_files:
        st.write(f"- {file.name}")

    # Mixing section
    if st.button("Mix & Play"):
        if len(uploaded_files) < 2:
            st.warning("Please upload at least 2 files to mix")
        else:
            with st.spinner("Mixing audio..."):
                try:
                    # Clean up previous files
                    cleanup()
                    
                    # Save new temporary files
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                            tmp.write(uploaded_file.read())
                            temp_files.append(tmp.name)
                    
                    # Load and mix audio
                    tracks = [AudioSegment.from_mp3(f) for f in temp_files]
                    max_length = max(len(track) for track in tracks)
                    mixed = AudioSegment.silent(duration=max_length)
                    
                    for track in tracks:
                        track = track + AudioSegment.silent(duration=max_length - len(track))
                        mixed = mixed.overlay(track)
                    
                    # Save mixed audio
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mixed_tmp:
                        mixed.export(mixed_tmp.name, format="mp3")
                        mixed_audio_path = mixed_tmp.name
                    
                    # Start playback thread
                    thread = threading.Thread(target=play_audio)
                    thread.start()
                    
                    st.success("Playing mixed audio!")
                except Exception as e:
                    st.error(f"Error: {e}")
                    cleanup()

    if st.button("Stop Playback"):
        pygame.mixer.music.stop()
        is_playing = False
        st.warning("Playback stopped")
else:
    st.info("Please upload some MP3 files to mix")