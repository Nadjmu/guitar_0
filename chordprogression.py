import streamlit as st

# Define the Chord class
class Chord:
    def __init__(self, root_note: str, interval: list[int]):
        self.root_note = root_note
        self.interval = interval

    def __str__(self):
        return f"{self.root_note} {self.interval}"

# Initialize session state variables
if 'chord_list' not in st.session_state:
    st.session_state.chord_list = []
if 'recording' not in st.session_state:
    st.session_state.recording = False  # Toggle to track recording state

# Dummy data for testing
allowed_chords = [["C", "maj"], ["G", "maj"], ["A", "min"], ["F", "maj"]]
allowed_chords_num = [[0, 4, 7], [0, 4, 7], [0, 3, 7], [0, 4, 7]]

# Toggle chord progression recording
if st.button("Generate Chord Progression"):
    if not st.session_state.recording:
        st.session_state.recording = True
        st.session_state.chord_list = []  # Clear list to start a new progression
        st.success("Recording started! Select chords.")
    else:
        st.session_state.recording = False
        st.success("Chord progression cleared!")

# Add chords if recording
if st.session_state.recording:
    st.write("### Select Chords for the Progression:")
    for i, chord in enumerate(allowed_chords):
        if st.button(','.join(chord), key=f"chord_{i}"):
            st.session_state.chord_list.append(Chord(chord[0], allowed_chords_num[i]))
            st.success(f"Added chord: {chord[0]} {allowed_chords_num[i]}")

# Display the chord progression
if st.session_state.chord_list:
    st.write("### Current Chord Progression:")
    for chord in st.session_state.chord_list:
        st.write(str(chord))
