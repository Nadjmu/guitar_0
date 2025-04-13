from pydub import AudioSegment
import os

mp3_folder = "audio_mp3"  # Folder with your MP3s
wav_folder = "audio_wav"  # Output folder for WAVs

# Convert all MP3s to WAVs
for filename in os.listdir(mp3_folder):
    if filename.endswith(".mp3"):
        mp3_path = os.path.join(mp3_folder, filename)
        wav_path = os.path.join(wav_folder, f"{os.path.splitext(filename)[0]}.wav")
        AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")
print("Conversion complete!")