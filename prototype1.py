from PIL import Image, ImageDraw
import streamlit as st
from fretboard import draw_fretboard
from io import BytesIO
import numpy as np 

st.set_page_config(layout="wide")

chromatic_scale = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
modes = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Myxolodian', 'Aoelian', 'Locrian']
chord_type = ['Major', 'Minor', 'Diminished', 'Augmented']
chord_type_abbr = ['maj', 'min', 'dim', 'aug']

def createFretboardNotes():
    notes = ['E', 'A', 'D', 'G', 'B', 'E']  # Open string notes for standard tuning
    fretboard_notes = []
    for string in range(6):
        string_notes = []
        start_note = notes[string]
        start_index = chromatic_scale.index(start_note)

        for fret in range(12 + 1):
            note_index = (start_index + fret) % 12 
            note = chromatic_scale[note_index]
            string_notes.append(note)
        fretboard_notes.append(string_notes)
    return fretboard_notes

fretboard_notes = createFretboardNotes()
###helper functions###
def save_plot_as_file(fig, file_format="png"):
    buffer = BytesIO()
    fig.savefig(buffer, format=file_format)
    buffer.seek(0)
    return buffer

###Test function input(root, index_list) output: triad in chromatic scale
def triadChromatic(root, index_list):
    index_of_root = chromatic_scale.index(root)
    third = chromatic_scale[(index_of_root+index_list[1]) % 12]
    fifth = chromatic_scale[(index_of_root+index_list[2]) % 12]
    return [root, third, fifth]

####Test algorithm input(root, chord_type) output: [0,4,7], [C,E,G]
def triad(root,chord_type):
    index_list =[0]
    if chord_type=='Major':
        index_list.append(4)
        index_list.append(7)
    elif chord_type=='Minor':
        index_list.append(3)
        index_list.append(7)
    elif chord_type=='Diminished':
        index_list.append(3)
        index_list.append(6)
    elif chord_type=='Augmented':
        index_list.append(4)
        index_list.append(8)
    triad_chromatic = triadChromatic(root, index_list)
    return index_list, triad_chromatic

###Test function input([C,E,G]) output: [[x,y], .... ] where [x,y]=='C' or 'E' or 'G'
def getHighlightedNotes(triad_chromatic):
    indices = []
    for note in triad_chromatic:
        for x, row in enumerate(fretboard_notes):
            for y, value in enumerate(row):
                if value == note:
                    indices.append([x,y])
    indices = [[y,x] for x, y in indices]
    return indices

# Set up session state variables
if 'show_notes' not in st.session_state:
    st.session_state.show_notes = True  # Initialize state to show the ellipse
if 'root' not in st.session_state:
        st.session_state['root'] = None
if 'chord_type' not in st.session_state: 
        st.session_state['chord_type'] = None
if 'mode' not in st.session_state: 
        st.session_state['mode'] = None

# Using containers for vertical organization
intro_container = st.container()
with intro_container:
    st.title("Guitar_0")
    st.write("This application serves as an interactive handbook for anyone trying to learn how to improvise. Pick a scale, a root note and the mode you want to play.")
    st.write("You will see all the possible chords which are allowed. Furthermore you can see possible and commonly used chord progressions")
    st.write("The visual guitar shows you where you have to land your fingers on the fretboard. It is particularly useful for people trying to switch from the piano to the guitar.")

# Layout with left sidebar, main content, and right sidebar
root ,scale_mode, chords, fretboard_col, spacer = st.columns([0.5,1,1,4,0.5])  # Adjust the ratio as needed

with root:
    with st.container():
        st.subheader("Root")
        for note in chromatic_scale:
            if st.button(note):#, key=f"root_{note}"):
                st.session_state['root'] = note
        if st.session_state['root']:
            st.write("root is:", st.session_state['root'])
    
with scale_mode:
    with st.container():
        st.subheader("Chord Types")
        for chord in chord_type:
            if st.button(chord):#, key=f"chord_{chord}"):
                st.session_state['chord_type'] = chord
                st.session_state['mode'] = None
        if st.session_state['chord_type']:
            st.write("chord is:", st.session_state['chord_type'])
    
    with st.container():
        st.subheader("Scale & Mode")
        for mode in modes: 
            if st.button(mode):#, key=f"mode_{mode}"):
                st.session_state['mode'] = mode
                st.session_state['chord_type'] = None
        if st.session_state['mode']:
            st.write("mode is:", st.session_state['mode'])

#print(st.session_state)
with chords:
    with st.container():
        if st.session_state['root'] and st.session_state['chord_type']:
            index_list, triad_chromatic = triad(st.session_state['root'], st.session_state['chord_type'])
            st.subheader(f"{st.session_state['root']}{chord_type_abbr[chord_type.index(st.session_state['chord_type'])]} ({triad_chromatic[0]} {triad_chromatic[1]} {triad_chromatic[2]})")
            if st.button("Extended Chord"):
                pass
with spacer: 
    button4 = st.button("Show Notes")
    button5 = st.button("Hide Notes")
    button6 = st.button("Button 6")
    if button4:
        st.write("Button 4 was pressed")
        st.session_state.show_notes = True
    elif button5:
        st.write("Button 5 was pressed")
        st.session_state.show_notes = False

##################FRETBOARDS#################
a_minor = [[0,1],[2,2],[2,3],[1,4],[0,5]]
fretboard_figures = [
    draw_fretboard(show_notes=st.session_state.show_notes, chord = a_minor),
    draw_fretboard(show_notes=st.session_state.show_notes, chord = a_minor),
    draw_fretboard(show_notes=st.session_state.show_notes, chord = a_minor),
]


with fretboard_col:
    with st.container():
        index_list, triad_chromatic = triad(st.session_state['root'], st.session_state['chord_type'])
        st.write(f"{st.session_state['root']}{chord_type_abbr[chord_type.index(st.session_state['chord_type'])]} ({triad_chromatic[0]} {triad_chromatic[1]} {triad_chromatic[2]})")
        highlighted_notes = getHighlightedNotes(triad_chromatic)
        fig = draw_fretboard(show_notes=st.session_state.show_notes, chord = highlighted_notes)
        fig1 = draw_fretboard(show_notes=st.session_state.show_notes, chord = highlighted_notes)
        st.pyplot(fig)
        st.pyplot(fig1)
"""
    for i, fig in enumerate(fretboard_figures):
        st.pyplot(fig)


        st.download_button(
            label=f"Download Fretboard1 {i + 1} as PDF",
            data=save_plot_as_file(fig, file_format="pdf"),
            file_name=f"fretboard_{i + 1}.pdf",
            mime="application/pdf"
        )
"""


# Using an expander for additional options
options_expander = st.expander("Advanced Options")
with options_expander:
    st.checkbox("Show Grid Lines")
    st.checkbox("Enable Editing Mode")

# Footer or additional info section
footer_container = st.container()
with footer_container:
    st.write("Created by Your Name - 2024")
    st.write("Additional information, links, or tutorials can be placed here.")