import streamlit as st
import streamlit.components.v1 as components
from music_theory import chromatic_scale, all_notes, chord_type, chord_type_abbr, scale_type, modes, intervals
from music_diagram import draw_music_diagram
from fretboard import draw_fretboard
from io import BytesIO
import time
from pygame import mixer
import os

st.set_page_config(layout="wide")  # Must be the first Streamlit command

mixer.init()

# Initialize session state
if "button_states_notes_tab" not in st.session_state:
    st.session_state.button_states_notes_tab = {} # {button_key: {'state': False, 'order': None}}

if 'button_press_order_notes_tab' not in st.session_state:
    st.session_state.button_press_order_notes_tab = []  # Tracks the sequence of pressed buttons

if 'button_states_chords_tab' not in st.session_state:
    st.session_state.button_states_chords_tab = {}
# Initialize session state
if 'chords_expander_label' not in st.session_state:
    st.session_state.chords_expander_label = "Root"

if 'scales_expander_label' not in st.session_state:
    st.session_state.scales_expander_label = "Root"



if 'button_states_scales_tab' not in st.session_state:
    st.session_state.button_states_scales_tab = {}

if 'chords_tab_chord_list' not in st.session_state:
    st.session_state.chords_tab_chord_list = []

if 'scales_tab_chord_list' not in st.session_state:
    st.session_state.scales_tab_chord_list = []


unpressed_colour = "#FFFFFF"  # White
pressed_colour = "#B0B0B0"    # Grey
pressed_text_colour = "white"
unpressed_text_colour = "black"
clef_image_path = "clef.png"  # Path to uploaded clef image

# Add some styling
st.markdown("""
<style>
    /* Style the expander header */
    .streamlit-expanderHeader {
        font-size: 18px;
        font-weight: bold;
        padding: 0.5rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
    }
    
    /* Style the buttons inside the expander */
    .stButton>button {
        width: 100%;
        margin: 0.25rem 0;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateX(5px);
    }
</style>
""", unsafe_allow_html=True)

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
fretboard_ids = {}
current_id = 1  # Start counting at 1

##initialize fretboard ids ###
for string in range(6):  # Process strings in order (0-5)
    for fret in range(13):  # Process frets in order (0-12)
        base_ids = [1,6,11,16,20,25]
        current_id = base_ids[string]+fret
        
        # Assign new ID (never reuse, even for same note in different octaves)
        fretboard_ids[(fret, string)] = current_id

# Define the Chord class
class Chord:
    def __init__(self, root_note: str, interval: list[int]):
        self.root_note = root_note
        self.interval = interval

    def __str__(self):
        return f"{self.root_note} {self.interval}"
    


# Function to add a new Chord to the list
def addChordChordsTab(root, interval):
    new_chord = Chord(root, interval)
    st.session_state.chords_tab_chord_list.append(new_chord)

# Function to add a new Chord to the list
def addChordScalesTab(root, interval):
    new_chord = Chord(root, interval)
    st.session_state.scales_tab_chord_list.append(new_chord)


###Test function input(root, index_list) output: triad in chromatic scale e.g. [C,E,G]
def getTriadChromatic(root, index_list):
    index_of_root = chromatic_scale.index(root)
    third = chromatic_scale[(index_of_root+index_list[1]) % 12]
    fifth = chromatic_scale[(index_of_root+index_list[2]) % 12]
    return [root, third, fifth]

####Test function map chord type to interval list -- input(root, chord_type) output: [0,4,7]
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




def ChangeButtonColour(widget_label, prsd_status): #GLOBAL
    btn_bg_colour = pressed_colour if prsd_status == True else unpressed_colour
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.background = '{btn_bg_colour}'
                }}
            }}
        </script>
        """
    components.html(f"{htmlstr}", height=0, width=0)



def NotesTabChkBtnStatusAndAssignColour(): #Notes
    list_notes_key = list(all_notes.keys())
    for i in range(len(list_notes_key)):
        #print(list(all_notes.keys()))
        ChangeButtonColour(list_notes_key[i], st.session_state.button_states_notes_tab[list_notes_key[i]]['state'])

def btn_pressed_callback_notes_tab(button_key): #Nnotes
    current_state = st.session_state.button_states_notes_tab[button_key]['state']
    st.session_state.button_states_notes_tab[button_key]['state'] = not current_state
    # Update press order if being activated
    if not current_state:  # If was False and now True (being activated)
        st.session_state.button_states_notes_tab[button_key]['order'] = len(st.session_state.button_press_order_notes_tab)
        st.session_state.button_press_order_notes_tab.append(button_key)
    else:  # If being deactivated
        if button_key in st.session_state.button_press_order_notes_tab:
            st.session_state.button_press_order_notes_tab.remove(button_key)
 
def ChordsTabChkBtnStatusAndAssignColour(id = ""): #Chords
    if id == 'R':
        list_root_key = ['CTR' + note for note in chromatic_scale]
        for i in range(len(list_root_key)):
            ChangeButtonColour(chromatic_scale[i],st.session_state.button_states_chords_tab[list_root_key[i]]['state'])
    elif id == 'T':
        list_chordtype_key = ['CTT' + chord for chord in chord_type]
        for i in range(len(list_chordtype_key)):
            ChangeButtonColour(chord_type[i],st.session_state.button_states_chords_tab[list_chordtype_key[i]]['state'])

def ChordsTabResetRootStatus(id = ""): #Chords
    list_root_key = ['CTR' + note for note in chromatic_scale]
    list_chordtype_key = ['CTT' + chord for chord in chord_type]

    if id == 'R':
        for i in range(len(list_root_key)):
            st.session_state.button_states_chords_tab[list_root_key[i]]['state'] = False
    elif id=='T':
        for i in range(len(list_chordtype_key)):
            st.session_state.button_states_chords_tab[list_chordtype_key[i]]['state'] = False

def btn_pressed_callback_chords_tab(button_key): #Chords
    if (button_key[2]=='R'):
        st.session_state.chords_expander_label = button_key[3:]
    current_state = st.session_state.button_states_chords_tab[button_key]['state']
    st.session_state.button_states_chords_tab[button_key]['state'] = not current_state
    # Update press order if being activated
    if not current_state:  # If was False and now True (being activated)
        ChordsTabResetRootStatus(button_key[2])
        st.session_state.button_states_chords_tab[button_key]['state'] = not current_state
    

def ScalesTabChkBtnStatusAndAssignColour(id = ""): #Scales
    if id == 'R':
        list_root_key = ['STR' + note for note in chromatic_scale]
        for i in range(len(list_root_key)):
            ChangeButtonColour(chromatic_scale[i],st.session_state.button_states_scales_tab[list_root_key[i]]['state'])
    elif id == 'D':
        list_modetype_key = ['STMD' + mode for mode in modes[0]]
        for i in range(len(list_modetype_key)):
            ChangeButtonColour(modes[0][i],st.session_state.button_states_scales_tab[list_modetype_key[i]]['state'])
    elif id == 'H':
        list_modetype_key = ['STMH' + mode for mode in modes[1]]
        for i in range(len(list_modetype_key)):
            ChangeButtonColour(modes[1][i],st.session_state.button_states_scales_tab[list_modetype_key[i]]['state'])

def ScalesTabResetRootStatus(id = ""): #Scales
    list_root_key = ['STR' + note for note in chromatic_scale]
    list_diatonic_modetype_key = ['STMD' + mode for mode in modes[0]]
    list_harmonicminor_modetype_key = ['STMH' + mode for mode in modes[1]]

    if id == 'R':
        for i in range(len(list_root_key)):
            st.session_state.button_states_scales_tab[list_root_key[i]]['state'] = False
    elif id=='M':
        for i in range(len(list_diatonic_modetype_key)):
            st.session_state.button_states_scales_tab[list_diatonic_modetype_key[i]]['state'] = False
        for i in range(len(list_harmonicminor_modetype_key)):
            st.session_state.button_states_scales_tab[list_harmonicminor_modetype_key[i]]['state'] = False

def btn_pressed_callback_scales_tab(button_key): #Scales
    if (button_key[2]=='R'):
        st.session_state.scales_expander_label = button_key[3:]
    current_state = st.session_state.button_states_scales_tab[button_key]['state']
    st.session_state.button_states_scales_tab[button_key]['state'] = not current_state
    # Update press order if being activated
    if not current_state:  # If was False and now True (being activated)
        st.session_state.scales_tab_chord_list = [] ###
        ScalesTabResetRootStatus(button_key[2])
        st.session_state.button_states_scales_tab[button_key]['state'] = not current_state

def AllowedChordsChtBtnStatusAndAssignColour(length, button_labels = []):
    list_keys = [f"chord_{i}" for i in range(length)]
    for i in range(len(list_keys)):
        ChangeButtonColour(button_labels[i],st.session_state.button_states_scales_tab[list_keys[i]]['state'])


def btn_pressed_callback_allowed_chords(button_key, chord_obj): #Scales
    current_state = st.session_state.button_states_scales_tab[button_key]['state']
    st.session_state.button_states_scales_tab[button_key]['state'] = not current_state
    if not current_state:
        st.session_state.scales_tab_chord_list.append(chord_obj)
    else:
        for i, chord in enumerate(st.session_state.scales_tab_chord_list):
            if chord.root_note == chord_obj.root_note and chord.interval == chord_obj.interval:
                st.session_state.scales_tab_chord_list.pop(i)
                break

def has_active_ctr_and_ctt():      #Chords 
    # Check if the dictionary exists
    if 'button_states_chords_tab' not in st.session_state:
        return False
    
    # Initialize flags
    has_active_ctr = False
    has_active_ctt = False
    
    # Iterate through all buttons
    for key, state_dict in st.session_state.button_states_chords_tab.items():
        if state_dict.get('state', False):  # Only check active buttons
            if key.startswith('CTR'):
                has_active_ctr = True
            elif key.startswith('CTT'):
                has_active_ctt = True
        
        # Early exit if both found
        if has_active_ctr and has_active_ctt:
            return True
    
    return has_active_ctr and has_active_ctt

def get_root_ctr_key(): #Output: C, D, E, ... #Chords 
    if 'button_states_chords_tab' not in st.session_state:
        return None
    
    for key, state_dict in st.session_state.button_states_chords_tab.items():
        if key.startswith('CTR') and state_dict.get('state', False):
            return key[3:]  # Returns the root
    return None

def get_chordtype_ctr_key(): #Output: Major, Minor, ... #Chords 
    if 'button_states_chords_tab' not in st.session_state:
        return None
    
    for key, state_dict in st.session_state.button_states_chords_tab.items():
        if key.startswith('CTT') and state_dict.get('state', False):
            return key[3:]  # Returns the root
    return None

def has_active_str_and_stm():      #Scales 
    # Check if the dictionary exists
    if 'button_states_scales_tab' not in st.session_state:
        return False
    
    # Initialize flags
    has_active_str = False
    has_active_stm = False
    
    # Iterate through all buttons
    for key, state_dict in st.session_state.button_states_scales_tab.items():
        if state_dict.get('state', False):  # Only check active buttons
            if key.startswith('STR'):
                has_active_str = True
            elif key.startswith('STM'):
                has_active_stm = True
        
        # Early exit if both found
        if has_active_str and has_active_stm:
            return True
    
    return has_active_str and has_active_stm

def get_root_str_key(): #Output: C, D, E, ... #Scales 
    if 'button_states_scales_tab' not in st.session_state:
        return None
    
    for key, state_dict in st.session_state.button_states_scales_tab.items():
        if key.startswith('STR') and state_dict.get('state', False):
            return key[3:]  # Returns the root
    return None

def get_scaletype_str_key(): #Output: C, D, E, ... #Chords 
    if 'button_states_scales_tab' not in st.session_state:
        return "",""
    
    for key, state_dict in st.session_state.button_states_scales_tab.items():
        if key.startswith('STM') and state_dict.get('state', False):
            if key[3]=='H':
                return "Harmonic Minor", key[4:]
            elif key[3]=='D':
                return "Diatonic", key[4:]
    return "", ""


####################
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
###Test function input(root,mode)
def createMode(root,mode,modes_type):
    mode_number = modes_type.index(mode)
    mode_interval_L = []
    ## Here diationic_intervals and %7 will change to be more general
    if modes_type == modes[0]:
        mode_interval_L = [intervals[0][(mode_number+i)%7] for i in range(7)]     # permutation of ['W','W','H','W','W','W','H']
    elif modes_type == modes[1]:
        mode_interval_L = [intervals[1][(mode_number+i)%7] for i in range(7)]
    
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
    #print(roman_numerals)
    return scale, mode_interval_L, mode_interval_num, allowed_chords, allowed_chords_num, roman_numerals    #return [C,D,E,F,G,A,B],[W,W,H,W,W,W,H],[2,2,1,2,2,2,1],[[C,E,G],...],[[0,4,7],...]

#######################################For fretboard##############
def keyToCoordinates(notes=["E4"]):     #Notes 
    coordinates = []
    for i, note in enumerate(notes):
        id_note = 1 + list(all_notes.keys()).index(note)
        # Extend coordinates with all matching positions for this note
        coordinates.extend(
            [fret, string, i] 
            for (fret, string), id_val in fretboard_ids.items() 
            if id_val == id_note
        )
    return coordinates

def initNotesButtons():     #Notes 
    for i in range(12):
        for j in range(3):
            note = chromatic_scale[(4 + i) % 12]
            new_octave = (4+i)//12
            button_key = f"{note}{j+new_octave+2}"
            # Initialize state if not exists
            if button_key not in st.session_state.button_states_notes_tab:
                st.session_state.button_states_notes_tab[button_key] = {'state': False, 'order': None}
            if j==0:
                with key_1_col:
                    # Create button with dynamic class
                    button = st.button(button_key, key=button_key, on_click=btn_pressed_callback_notes_tab, args=(button_key,))
            elif j==1:
                with key_2_col:
                    # Create button with dynamic class
                    button = st.button(button_key, key=button_key, on_click=btn_pressed_callback_notes_tab, args=(button_key,))
            elif j==2:
                with key_3_col:
                    # Create button with dynamic class
                    button = st.button(button_key, key=button_key, on_click=btn_pressed_callback_notes_tab, args=(button_key,))

# Sidebar navigation
with st.sidebar:
    selected = st.radio(
        "",
        ["Notes", "Chords", "Scales"],
        index=0
    )

# Main content area
if selected == "Notes":
    st.title("Notes 🪕 ")
    st.header("This is the notes section")
    key_1_col, key_2_col, key_3_col, music_diagram_col, fretboard_col = st.columns([1,1,1,8,13])
    initNotesButtons()   #initializes the buttons in the key_1_col - key_3_col
    NotesTabChkBtnStatusAndAssignColour()

    with music_diagram_col:
        with st.container():
            #for i in range(12):
            #    st.write("")

            # Get notes_notes_tab in activation order:
            notes_notes_tab = [key for key in st.session_state.button_press_order_notes_tab if st.session_state.button_states_notes_tab[key]['state'] is True]
            figures = []
            # Play the MP3 file when the button is clicked
            # Play a sequence of MP3 files when the button is clicked
            if st.button("▶ ", key="play_notes_sequence"):
                audio_files = [f"audio_mp3/{note}.mp3" for note in notes_notes_tab]  # List of MP3 file paths
                for audio_file_path in audio_files:
                    if os.path.exists(audio_file_path):  # Check if the file exists
                        #st.write(f"Now playing: {audio_file_path.split('/')[-1]}")  # Display the file being played
                        mixer.music.load(audio_file_path)  # Load the MP3 file
                        mixer.music.play()  # Play the MP3 file

                        # Wait for the current file to finish playing
                        while mixer.music.get_busy():
                            time.sleep(0.1)
            fig = draw_music_diagram(notes_notes_tab, clef_image_path)
            figures.append(fig)
            st.pyplot(fig)
    
    with fretboard_col:
        with st.container():
            for i in range(6):
                st.write("")

            coordinates_notes_notes_tab = keyToCoordinates(notes_notes_tab)
            figures = []
            fig = draw_fretboard(True, coordinates_notes_notes_tab)
            figures.append(fig)
            st.pyplot(fig)

elif selected == "Chords":
    st.title("Chords")
    st.write("This is the chords section")
    with st.container():
        st.markdown("""
    <hr style="border: none; height: 2px; background-color: #ccc; margin: 0; padding: 0;">
""", unsafe_allow_html=True)
        des_col, root_col, fill_col = st.columns([1,2,15])
        with des_col:
            st.subheader("Root: ")
        with root_col:
            # Add custom CSS for the "Root" expander
            st.markdown("""
                <style>
                /* Target the expander with the label "Root" */
                div[aria-expanded="false"] > div:first-child {
                    font-size: 20px; /* Adjust font size */
                    font-weight: bold; /* Make it bold */
                    padding: 10px; /* Add padding */
                    background-color: #f0f2f6; /* Background color */
                    border-radius: 10px; /* Rounded corners */
                }
                </style>
            """, unsafe_allow_html=True)
            with st.expander(st.session_state.chords_expander_label,expanded=False):
                for note in chromatic_scale:
                    button_key = f"CTR{note}"
                    if button_key not in st.session_state.button_states_chords_tab:
                        st.session_state.button_states_chords_tab[button_key] = {'state': False}
                    
                    button = st.button(note, key=button_key, on_click=btn_pressed_callback_chords_tab, args=(button_key,))
        st.markdown("""
    <hr style="border: none; height: 2px; background-color: #ccc; margin: 0; padding: 0;">
""", unsafe_allow_html=True)
    # Layout with left sidebar, main content, and right sidebar
    type_col, info_col, fretboard_col = st.columns([3,5,13])  # Adjust the ratio as needed

    with type_col:
        with st.expander("Chord Type",expanded=False):
            for chord in chord_type:
                button_key = f"CTT{chord}" #stands for Chord Tab Type
                if button_key not in st.session_state.button_states_chords_tab:
                    st.session_state.button_states_chords_tab[button_key] = {'state': False}
                
                button = st.button(chord, key=button_key, on_click=btn_pressed_callback_chords_tab, args=(button_key,))
            ChordsTabChkBtnStatusAndAssignColour("T")

    with info_col:
        root = get_root_ctr_key()
        chord_type_1 = get_chordtype_ctr_key()
        if has_active_ctr_and_ctt():
            interval_list = getIntervalList(root, chord_type_1)
            triad_chromatic = getTriadChromatic(root, interval_list)
            #print("triad chromatic: ",triad_chromatic)
            st.session_state.chords_tab_chord_list = [] #reset list
            addChordChordsTab(root, interval_list)
            st.subheader(f"{root}{chord_type_abbr[chord_type.index(chord_type_1)]} ({triad_chromatic[0]} {triad_chromatic[1]} {triad_chromatic[2]})")
            # Get notes in activation order:
            notes = [note + ('3' if chromatic_scale.index(note) >= chromatic_scale.index(triad_chromatic[0]) else '4')
    for note in triad_chromatic]
            #print("notes:  ",notes)
            figures = []
            if st.button("▶ ", key="play_scales_sequence"):
                audio_files = [f"audio_mp3/{note}.mp3" for note in notes]  # List of MP3 file paths
                for audio_file_path in audio_files:
                    #st.write(f"Now playing: {audio_file_path.split('/')[-1]}")  # Display the file being played
                    mixer.music.load(audio_file_path)  # Load the MP3 file
                    mixer.music.play()  # Play the MP3 file

                    # Wait for the current file to finish playing
                    while mixer.music.get_busy():
                        time.sleep(0.1)
            fig = draw_music_diagram(notes, clef_image_path)
            figures.append(fig)
            st.pyplot(fig)

    with fretboard_col:
        for i in range(3):
            st.write("")
        figures = []
        if st.session_state.chords_tab_chord_list:
            for displayed_chord in st.session_state.chords_tab_chord_list:
                triad_chromatic = getTriadChromatic(displayed_chord.root_note, displayed_chord.interval)
                highlighted_notes = getHighlightedNotes(triad_chromatic)
                fig = draw_fretboard(show_notes=True, highlighted_notes = highlighted_notes)
                figures.append(fig)

            for i,fig in enumerate(figures):
                st.pyplot(fig)

elif selected == "Scales":
    st.title("Scales")
    st.write("This is the scales section")
    with st.container():
        st.markdown("""
    <hr style="border: none; height: 2px; background-color: #ccc; margin: 0; padding: 0;">
""", unsafe_allow_html=True)
        des_col, root_col, fill_col = st.columns([1,2,15])
        with des_col:
            st.subheader("Root: ")
        with root_col:
            # Add custom CSS for the "Root" expander
            st.markdown("""
                <style>
                /* Target the expander with the label "Root" */
                div[aria-expanded="false"] > div:first-child {
                    font-size: 20px; /* Adjust font size */
                    font-weight: bold; /* Make it bold */
                    padding: 10px; /* Add padding */
                    background-color: #f0f2f6; /* Background color */
                    border-radius: 10px; /* Rounded corners */
                }
                </style>
            """, unsafe_allow_html=True)
            with st.expander(st.session_state.scales_expander_label,expanded=False):
                for note in chromatic_scale:
                    button_key = f"STR{note}"
                    if button_key not in st.session_state.button_states_scales_tab:
                        st.session_state.button_states_scales_tab[button_key] = {'state': False}
                    
                    button = st.button(note, key=button_key, on_click=btn_pressed_callback_scales_tab, args=(button_key,))
        st.markdown("""
    <hr style="border: none; height: 2px; background-color: #ccc; margin: 0; padding: 0;">
""", unsafe_allow_html=True)
    # Layout with left sidebar, main content, and right sidebar
     # Layout with left sidebar, main content, and right sidebar
    type_col, info_col, fretboard_col = st.columns([2,5,13])  # Adjust the ratio as needed
    
    with type_col:
        st.subheader("Scale Type: ")
        with st.expander("Diatonic", expanded=False):
            for mode in modes[0]:
                button_key = f"STMD{mode}" #stands for Scales Tab Mode Diatonic
                if button_key not in st.session_state.button_states_scales_tab:
                    st.session_state.button_states_scales_tab[button_key] = {'state': False}

                button = st.button(mode, key=button_key, on_click=btn_pressed_callback_scales_tab, args=(button_key,))
            ScalesTabChkBtnStatusAndAssignColour("D")

        with st.expander("Harmonic Minor", expanded=False):
            for mode in modes[1]:
                button_key = f"STMH{mode}" #stands for Scales Tab Mode Harmonic Minor
                if button_key not in st.session_state.button_states_scales_tab:
                    st.session_state.button_states_scales_tab[button_key] = {'state': False}

                button = st.button(mode, key=button_key, on_click=btn_pressed_callback_scales_tab, args=(button_key,))
            ScalesTabChkBtnStatusAndAssignColour("H")
    
    with info_col:
        root = get_root_str_key()
        scale_type_1, mode_1 = get_scaletype_str_key()
        if has_active_str_and_stm():
            scale = []
            allowed_chords = []
            allowed_chords_num = []

            st.subheader(root+" "+scale_type_1+" "+mode_1)
            if scale_type_1=="Diatonic":
                scale, mode_interval_L, mode_interval_num, allowed_chords, allowed_chords_num, roman_numerals = createMode(root,mode_1,modes[0])
            elif scale_type_1=="Harmonic Minor":
                scale, mode_interval_L, mode_interval_num, allowed_chords, allowed_chords_num, roman_numerals = createMode(root,mode_1,modes[1])
            
            st.write(" - ".join(scale))
            notes_scales = [
    note + ('3' if chromatic_scale.index(note) >= chromatic_scale.index(scale[0]) else '4')
    for note in scale
]
            notes_scales.append(scale[0]+'4')
            figures = []
            # Play the MP3 file when the button is clicked
            # Play a sequence of MP3 files when the button is clicked
            if st.button("▶ ", key="play_scales_sequence"):
                audio_files = [f"audio_mp3/{note}.mp3" for note in notes_scales]  # List of MP3 file paths
                for audio_file_path in audio_files:
                    #st.write(f"Now playing: {audio_file_path.split('/')[-1]}")  # Display the file being played
                    mixer.music.load(audio_file_path)  # Load the MP3 file
                    mixer.music.play()  # Play the MP3 file

                    # Wait for the current file to finish playing
                    while mixer.music.get_busy():
                        time.sleep(0.1)
            fig = draw_music_diagram(notes_scales, clef_image_path)
            st.pyplot(fig)
            ####Allowed Chords
            st.subheader("Allowed Chords")
            button_labels = []
            for i, chord in enumerate(allowed_chords):
                button_label = f"{roman_numerals[i]}: {','.join(chord)}"
                button_labels.append(button_label)
                button_key = f"chord_{i}"
                chord_obj = Chord(chord[0], allowed_chords_num[i])
                if button_key not in st.session_state.button_states_scales_tab:
                    st.session_state.button_states_scales_tab[button_key] = {'state': False}
                
                st.button(button_label, key=button_key, on_click=btn_pressed_callback_allowed_chords, args=(button_key,chord_obj,))
                if st.session_state.button_states_scales_tab[button_key]['state']:
                    triad_chromatic = getTriadChromatic(chord_obj.root_note, chord_obj.interval)
                    notes = [note + ('3' if chromatic_scale.index(note) >= chromatic_scale.index(triad_chromatic[0]) else '4')
    for note in triad_chromatic]
                    if st.button("▶ ", key=f"play_allowed_chord{i}"):
                        audio_files = [f"audio_mp3/{note}.mp3" for note in notes]  # List of MP3 file paths
                        for audio_file_path in audio_files:
                            #st.write(f"Now playing: {audio_file_path.split('/')[-1]}")  # Display the file being played
                            mixer.music.load(audio_file_path)  # Load the MP3 file
                            mixer.music.play()  # Play the MP3 file

                            # Wait for the current file to finish playing
                            while mixer.music.get_busy():
                                time.sleep(0.1)
                    fig1 = draw_music_diagram(notes, clef_image_path)
                    st.pyplot(fig1)
            
            AllowedChordsChtBtnStatusAndAssignColour(len(allowed_chords),button_labels)
            
    

    with fretboard_col:
        for i in range(13):
            st.write("")

        if has_active_str_and_stm():
            coordinates_notes_scales_tab = keyToCoordinates(notes_scales)
            figures = []
            fig = draw_fretboard(True, coordinates_notes_scales_tab)
            st.pyplot(fig)

            for i in range(4):
                st.write("")

            chord_labels = [] #I, ii°, ....
            for i,displayed_chord in  enumerate(st.session_state.scales_tab_chord_list):
                index = 0
                for k, chord in enumerate(allowed_chords):
                    if displayed_chord.root_note == chord[0]:
                        index = k
                label = (roman_numerals[index]+": "+str(displayed_chord))
                chord_labels.append(label)
                
                triad_chromatic = getTriadChromatic(displayed_chord.root_note, displayed_chord.interval)
                highlighted_notes = getHighlightedNotes(triad_chromatic)
                fig = draw_fretboard(show_notes=True, highlighted_notes = highlighted_notes)
                figures.append(fig)
            for i,fig in enumerate(figures):
                st.markdown("###### "+chord_labels[i])
                st.pyplot(fig)