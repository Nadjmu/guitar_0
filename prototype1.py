import streamlit as st
from fretboard import draw_fretboard
from io import BytesIO
import numpy as np 
import music_theory

st.set_page_config(layout="wide")

chromatic_scale = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
modes_diatonic = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Myxolodian', 'Aoelian', 'Locrian']
chord_type = ['Major', 'Minor', 'Diminished', 'Augmented']
chord_type_abbr = ['maj', 'min', 'dim', 'aug']
diatonic_intervals = ['W','W','H','W','W','W','H']
harmonic_minor_intervals = ['W','H','W','W','H','WH','H']
modes_harmonic_minor =['Harmonic Minor', 'Locrian', 'Ionian', 'Dorian', 'Phrygian Dominant', 'Lydian', 'Ultralocrian']

# Set up session state variables
if 'show_notes' not in st.session_state:
    st.session_state.show_notes = True  # Initialize state to show the ellipse
if 'root' not in st.session_state:
        st.session_state['root'] = None
if 'chord_type' not in st.session_state: 
        st.session_state['chord_type'] = None
if 'mode' not in st.session_state: 
        st.session_state['mode'] = None
if 'diatonic_scale' not in st.session_state:
    st.session_state['diatonic_scale'] = False
if 'harmonic_minor_scale' not in st.session_state:
    st.session_state['harmonic_minor_scale'] = False
if 'chord_list' not in st.session_state:
    st.session_state.chord_list = []
if 'recording' not in st.session_state:
    st.session_state.recording = False

# Define the Chord class
class Chord:
    def __init__(self, root_note: str, interval: list[int]):
        self.root_note = root_note
        self.interval = interval

    def __str__(self):
        return f"{self.root_note} {self.interval}"


# Function to add a new Chord to the list
def addChord(root, interval):
    new_chord = Chord(root, interval)
    st.session_state.chord_list.append(new_chord)

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
print(fretboard_notes)
###helper functions###
def save_plot_as_file(fig, file_format="png"):
    buffer = BytesIO()
    fig.savefig(buffer, format=file_format)
    buffer.seek(0)
    return buffer

###Test function input(root, index_list) output: triad in chromatic scale
def getTriadChromatic(root, index_list):
    index_of_root = chromatic_scale.index(root)
    third = chromatic_scale[(index_of_root+index_list[1]) % 12]
    fifth = chromatic_scale[(index_of_root+index_list[2]) % 12]
    return [root, third, fifth]

####Test function map chord type to interval list -- input(root, chord_type) output: [0,4,7], [C,E,G]
def getIntervalList(root,chord_type):
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
    return index_list

def get_roman_numerals(intervals):
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]  # Roman numerals for scale degrees
    result = []

    for i, interval in enumerate(intervals):
        if interval == [0, 4, 7]:  # Major chord
            result.append(roman_numerals[i])
        elif interval == [0, 3, 7]:  # Minor chord
            result.append(roman_numerals[i].lower())
        elif interval == [0, 3, 6]:
            result.append(roman_numerals[i].lower()+"°")
        elif interval == [0, 4, 8]:
            result.append(roman_numerals[i]+"+")
        else:
            result.append(f"Unknown({interval})")  # For unsupported intervals

    return result


###Test function input([C,E,G]) output: [[x,y], .... ] where [x,y]=='C' or 'E' or 'G'
def getHighlightedNotes(triad_chromatic):
    indices = []
    for i,note in enumerate(triad_chromatic):
        for x, row in enumerate(fretboard_notes):
            for y, value in enumerate(row):
                if value == note:
                    indices.append([x,y,i])
    indices = [[y,x,i] for x, y, i in indices]
    return indices



###Test function input(root,mode)
def createMode(root,mode,modes):
    mode_number = modes.index(mode)
    ## Here diationic_intervals and %7 will change to be more general
    if modes == modes_diatonic:
        mode_interval_L = [diatonic_intervals[(mode_number+i)%7] for i in range(7)]     # permutation of ['W','W','H','W','W','W','H']
    elif modes == modes_harmonic_minor:
        mode_interval_L = [harmonic_minor_intervals[(mode_number+i)%7] for i in range(7)]
    
    mode_interval_num = [                                                           # above in [2,2,1,2,2,2,1]
    2 if interval == 'W' else 1 if interval == 'H' else 3 if interval == 'WH' else None
    for interval in mode_interval_L
]
    root_index = chromatic_scale.index(root)
    scale = [chromatic_scale[(root_index + sum(mode_interval_num[:i])) % 12] for i in range(len(mode_interval_num))]
    #print(scale)
    allowed_chords = []
    for index, root in enumerate(scale): 
        allowed_chords.append([root,scale[(index+2)%7],scale[(index+4)%7]])
    #print(allowed_chords)
    allowed_chords_num=[]
    for chord in allowed_chords:
        interval_to_third = (chromatic_scale.index(chord[1])-chromatic_scale.index(chord[0]))%12
        interval_to_fifth = (chromatic_scale.index(chord[2])-chromatic_scale.index(chord[0]))%12
        allowed_chords_num.append([0,interval_to_third,interval_to_fifth])
    #print(allowed_chords_num)
    roman_numerals = get_roman_numerals(allowed_chords_num)
    print(roman_numerals)
    return scale, mode_interval_L, mode_interval_num, allowed_chords, allowed_chords_num, roman_numerals    #return [C,D,E,F,G,A,B],[W,W,H,W,W,W,H],[2,2,1,2,2,2,1],[[C,E,G],...],[[0,4,7],...]

##################FRONT END *******************************
# Using containers for vertical organization
intro_container = st.container()
with intro_container:
    st.title("Guitar_0")
    st.write("This application serves as an interactive handbook for anyone trying to learn how to improvise. Pick a scale, a root note and the mode you want to play.")
    st.write("You will see all the possible chords which are allowed. Furthermore you can see possible and commonly used chord progressions")
    st.write("The visual guitar shows you where you have to land your fingers on the fretboard. It is particularly useful for people trying to switch from the piano to the guitar.\n \n")

# Layout with left sidebar, main content, and right sidebar
root ,pick_scale, info, fretboard_col, spacer = st.columns([0.5,1,1,4,0.5])  # Adjust the ratio as needed

with root:
    with st.container():
        st.header("Root")
        for note in chromatic_scale:
            if st.button(note):#, key=f"root_{note}"):
                st.session_state['root'] = note
        if st.session_state['root']:
            st.write("root is:", st.session_state['root'])
    
with pick_scale:
    with st.container():            #Pick Chord Types
        st.header("Chord Types")
        for chord in chord_type:
            if st.button(chord):#, key=f"chord_{chord}"):
                st.session_state['chord_type'] = chord
                st.session_state['mode'] = None
        if st.session_state['chord_type']:
            st.write("chord is:", st.session_state['chord_type'])
    
    with st.container():            #Pick Diatonic Scale
        st.header("Scale")
        if st.button("Diatonic Scales"): #so far only diatonic scales
            st.session_state['diatonic_scale'] = not st.session_state['diatonic_scale']
        if st.session_state['diatonic_scale']:
            for mode in modes_diatonic : 
                if st.button(mode):#, key=f"mode_{mode}"):
                    st.session_state['mode'] = mode
                    st.session_state['chord_type'] = None
            if st.session_state['mode']:
                st.write("mode is:", st.session_state['mode'])
    with st.container():            #Pick Harmonic Minor Scale
        if st.button("Harmonic Minor Scales"): #so far only diatonic scales
            st.session_state['harmonic_minor_scale'] = not st.session_state['harmonic_minor_scale']
        if st.session_state['harmonic_minor_scale']:
            for mode in modes_harmonic_minor : 
                if st.button(mode):#, key=f"mode_{mode}"):
                    st.session_state['mode'] = mode
                    st.session_state['chord_type'] = None
            if st.session_state['mode']:
                st.write("mode is:", st.session_state['mode'])
        else:
            pass #here bugfix for ValueError: 'Phrygian' is not in list

#print(st.session_state)
with info:
    with st.container():
        if st.session_state['root'] and st.session_state['chord_type']:
            interval_list = getIntervalList(st.session_state['root'], st.session_state['chord_type'])
            triad_chromatic = getTriadChromatic(st.session_state['root'], interval_list)
            st.session_state.chord_list = [] #reset list
            addChord(st.session_state['root'], interval_list)
            st.subheader(f"{st.session_state['root']}{chord_type_abbr[chord_type.index(st.session_state['chord_type'])]} ({triad_chromatic[0]} {triad_chromatic[1]} {triad_chromatic[2]})")
            if st.button("Extended Chord"):
                pass

    with st.container():
        if st.session_state['root'] and st.session_state['mode']:
            scale = []
            allowed_chords = []
            allowed_chords_num = []

            if st.session_state['diatonic_scale']:
                scale, mode_interval_L, mode_interval_num, allowed_chords, allowed_chords_num, roman_numerals = createMode(st.session_state['root'],st.session_state['mode'],modes_diatonic)
            elif st.session_state['harmonic_minor_scale']:
                scale, mode_interval_L, mode_interval_num, allowed_chords, allowed_chords_num, roman_numerals = createMode(st.session_state['root'],st.session_state['mode'],modes_harmonic_minor)
            
            if st.session_state['diatonic_scale'] or st.session_state['harmonic_minor_scale']:
                st.header(f"{st.session_state['root']} {st.session_state['mode']}")
            #st.subheader('Interval Pattern')
            #st.caption(" - ".join(mode_interval_L))
                st.subheader("Notes in scale")
                st.caption(" - ".join(scale))
                st.subheader("Allowed Chords")
                for i, chord in enumerate(allowed_chords):
                    button_label = f"{roman_numerals[i]}: {','.join(chord)}"
                    if st.button(button_label,key=f"chord_{i}"):
                        if st.session_state.recording:
                            st.session_state.chord_list.append(Chord(chord[0], allowed_chords_num[i]))
                            st.success(f"Added chord: {chord[0]} {allowed_chords_num[i]}")
                        else:
                            st.session_state.chord_list = [] #reset list
                            addChord(chord[0], allowed_chords_num[i])

                if st.button("Generate Chord Progression"):
                    if not st.session_state.recording:
                        st.session_state.recording = True
                        st.session_state.chord_list = []
                        st.success("Select from the allowed chords to create your Chord Progression")
                    else:
                        st.session_state.recording = False
                        st.session_state.chord_list = []
                        st.success("Chord progression cleared!")
            
            # Display the chord progression
            if st.session_state.recording:
                st.write("### Current Chord Progression:")
                chord_label = []
                for displayed_chord in st.session_state.chord_list:
                    index = 0
                    for k,chord in enumerate(allowed_chords):
                        if displayed_chord.root_note == chord[0]:
                            index = k
                    label = (roman_numerals[index]+": "+str(displayed_chord))
                    chord_label.append(label)
                    st.write(label)

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


for i, chord in enumerate(st.session_state.chord_list):
    print(f"{i + 1}. Root Note: {chord.root_note}, Interval: {chord.interval}")

with fretboard_col:
    with st.container():
        figures = []
        if st.session_state.chord_list:
            for displayed_chord in st.session_state.chord_list:
                triad_chromatic = getTriadChromatic(displayed_chord.root_note, displayed_chord.interval)
                highlighted_notes = getHighlightedNotes(triad_chromatic)
                fig = draw_fretboard(show_notes=st.session_state.show_notes, highlighted_notes = highlighted_notes)
                figures.append(fig)

            for i,fig in enumerate(figures):
                if st.session_state['recording']:
                    st.markdown("###### "+chord_label[i])
                st.pyplot(fig)

# Using an expander for additional options
options_expander = st.expander("Advanced Options")
with options_expander:
    st.checkbox("Show Grid Lines")
    st.checkbox("Enable Editing Mode")

# Footer or additional info section
footer_container = st.container()
with footer_container:
    st.write("Created by Nadjmu - 2024")
    st.write("Additional information, links, or tutorials can be placed here.")

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
