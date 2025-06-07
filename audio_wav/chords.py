from pydub import AudioSegment

# Load your WAV files
note1 = AudioSegment.from_wav("E3.wav")
note2 = AudioSegment.from_wav("Ab3.wav")
note3 = AudioSegment.from_wav("C4.wav")

# Pad the shorter ones with silence so they are the same length
max_len = max(len(note1), len(note2), len(note3))
note1 = note1 + AudioSegment.silent(duration=max_len - len(note1))
note2 = note2 + AudioSegment.silent(duration=max_len - len(note2))
note3 = note3 + AudioSegment.silent(duration=max_len - len(note3))

# Overlay the notes to play them simultaneously
chord = note1.overlay(note2).overlay(note3)

# Export to a new file
chord.export("Eaug.wav", format="wav")
