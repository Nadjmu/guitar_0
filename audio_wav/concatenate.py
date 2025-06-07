import streamlit as st
import librosa
import soundfile as sf
import numpy as np
import tempfile
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# List of WAV files relative to the script's directory
wav_files = [os.path.join(current_dir, "C3.wav"), 
             os.path.join(current_dir, "E3.wav"), 
             os.path.join(current_dir, "G3.wav")]

# Verify that all files exist
for file in wav_files:
    if not os.path.exists(file):
        raise FileNotFoundError(f"File not found: {file}")

# Merge audio files
merged_audio = np.concatenate([librosa.load(f, sr=None)[0] for f in wav_files])  # Merge audio
sample_rate = librosa.load(wav_files[0], sr=None)[1]  # Get the sample rate from the first file

# Save the merged audio to a temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
    sf.write(tmp_file.name, merged_audio, sample_rate)  # Write the merged audio to the file
    st.audio(tmp_file.name)  # Play the audio file in Streamlit