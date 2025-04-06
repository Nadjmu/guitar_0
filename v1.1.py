import streamlit as st
import streamlit.components.v1 as components
from music_theory import chromatic_scale, all_notes, chord_type, chord_type_abbr
from music_diagram import draw_music_diagram
from fretboard import draw_fretboard
from io import BytesIO

st.set_page_config(layout="wide")  # Must be the first Streamlit command
# Initialize session state
if "button_states_notes_tab" not in st.session_state:
    st.session_state.button_states_notes_tab = {} # {button_key: {'state': False, 'order': None}}

if 'button_press_order_notes_tab' not in st.session_state:
    st.session_state.button_press_order_notes_tab = []  # Tracks the sequence of pressed buttons

if 'button_states_chords_tab' not in st.session_state:
    st.session_state.button_states_chords_tab = {}

if 'chord_list' not in st.session_state:
    st.session_state.chord_list = []
    
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
def addChord(root, interval):
    new_chord = Chord(root, interval)
    st.session_state.chord_list.append(new_chord)


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



def NotesTabChkBtnStatusAndAssignColour(): #NOT GLOBAL  because of list_notes_key dependent on notes_button
    list_notes_key = list(all_notes.keys())
    for i in range(len(list_notes_key)):
        #print(list(all_notes.keys()))
        ChangeButtonColour(list_notes_key[i], st.session_state.button_states_notes_tab[list_notes_key[i]]['state'])

def btn_pressed_callback_notes_tab(button_key): #NOT GlOBAL because of button_states_notes_tab
    # Toggle state
    current_state = st.session_state.button_states_notes_tab[button_key]['state']
    st.session_state.button_states_notes_tab[button_key]['state'] = not current_state
    # Update press order if being activated
    if not current_state:  # If was False and now True (being activated)
        st.session_state.button_states_notes_tab[button_key]['order'] = len(st.session_state.button_press_order_notes_tab)
        st.session_state.button_press_order_notes_tab.append(button_key)
    else:  # If being deactivated
        if button_key in st.session_state.button_press_order_notes_tab:
            st.session_state.button_press_order_notes_tab.remove(button_key)
 
def ChordsTabChkBtnStatusAndAssignColour():
    list_root_key = ['CTR' + note for note in chromatic_scale]
    for i in range(len(list_root_key)):
        ChangeButtonColour(chromatic_scale[i],st.session_state.button_states_chords_tab[list_root_key[i]]['state'])
    list_chordtype_key = ['CTT' + chord for chord in chord_type]
    for i in range(len(list_chordtype_key)):
        ChangeButtonColour(chord_type[i],st.session_state.button_states_chords_tab[list_chordtype_key[i]]['state'])

def ChordsTabResetRootStatus(id = ""):
    list_root_key = ['CTR' + note for note in chromatic_scale]
    list_chordtype_key = ['CTT' + chord for chord in chord_type]

    if id == 'R':
        for i in range(len(list_root_key)):
            st.session_state.button_states_chords_tab[list_root_key[i]]['state'] = False
    elif id=='T':
        for i in range(len(list_chordtype_key)):
            st.session_state.button_states_chords_tab[list_chordtype_key[i]]['state'] = False

def btn_pressed_callback_chords_tab(button_key):
    current_state = st.session_state.button_states_chords_tab[button_key]['state']
    st.session_state.button_states_chords_tab[button_key]['state'] = not current_state
    # Update press order if being activated
    if not current_state:  # If was False and now True (being activated)
        ChordsTabResetRootStatus(button_key[2])
        st.session_state.button_states_chords_tab[button_key]['state'] = not current_state

def has_active_ctr_and_ctt():
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

def get_root_ctr_key(): #Output: C, D, E, ...
    if 'button_states_chords_tab' not in st.session_state:
        return None
    
    for key, state_dict in st.session_state.button_states_chords_tab.items():
        if key.startswith('CTR') and state_dict.get('state', False):
            return key[3:]  # Returns the root
    return None

def get_chordtype_ctr_key(): #Output: C, D, E, ...
    if 'button_states_chords_tab' not in st.session_state:
        return None
    
    for key, state_dict in st.session_state.button_states_chords_tab.items():
        if key.startswith('CTT') and state_dict.get('state', False):
            return key[3:]  # Returns the root
    return None
#######################################For fretboard##############
def keyToCoordinates(notes=["E4"]):
    coordinates = []
    for i, note in enumerate(notes):
        id_note = 1 + list(all_notes.keys()).index(note)
        # Extend coordinates with all matching positions for this note
        coordinates.extend(
            [fret, string, i] 
            for (fret, string), id_val in fretboard_ids.items() 
            if id_val == id_note
        )
    print(coordinates)
    return coordinates

def initNotesButtons():
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
    st.title("Notes")
    intro_container = st.container()
    with intro_container:
        st.title("🪕 Guitar_0")
        st.write("here you will learn about notes. There are 36 possible notes you can play on the fretboard up to the 12th fret")
        st.write("This application serves as an interactive handbook for anyone trying to learn how to improvise. Pick a scale, a root note and the mode you want to play.")
        st.write("You will see all the possible chords which are allowed. Furthermore you can see possible and commonly used chord progressions")
        st.write("The visual guitar shows you where you have to land your fingers on the fretboard. It is particularly useful for people trying to switch from the piano to the guitar.\n \n")
    
    st.header("pick your note")
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
            fig = draw_music_diagram(notes_notes_tab, clef_image_path)
            figures.append(fig)
            st.pyplot(fig)
    
    with fretboard_col:
        with st.container():
            for i in range(3):
                st.write("")

            coordinates_notes_notes_tab = keyToCoordinates(notes_notes_tab)
            figures = []
            fig = draw_fretboard(True, coordinates_notes_notes_tab)
            figures.append(fig)
            st.pyplot(fig)

elif selected == "Chords":
    st.title("Chords")
    intro_container = st.container()
    with intro_container:
        st.title("🪕 Guitar_1")
        st.write("This application serves as an interactive handbook for anyone trying to learn how to improvise. Pick a scale, a root note and the mode you want to play.")
        st.write("You will see all the possible chords which are allowed. Furthermore you can see possible and commonly used chord progressions")
        st.write("The visual guitar shows you where you have to land your fingers on the fretboard. It is particularly useful for people trying to switch from the piano to the guitar.\n \n")
    
    # Layout with left sidebar, main content, and right sidebar
    root_col, type_col, info_col, fretboard_col = st.columns([2,3,5,13])  # Adjust the ratio as needed

    with root_col:
        with st.expander("Root",expanded=False):
            for note in chromatic_scale:
                button_key = f"CTR{note}" #stands for Chord Tab Root
                if button_key not in st.session_state.button_states_chords_tab:
                    st.session_state.button_states_chords_tab[button_key] = {'state': False}

                button = st.button(note, key=button_key, on_click=btn_pressed_callback_chords_tab, args=(button_key,))
            ChordsTabChkBtnStatusAndAssignColour()

    with type_col:
        with st.expander("Chord Type",expanded=False):
            for chord in chord_type:
                button_key = f"CTT{chord}" #stands for Chord Tab Type
                if button_key not in st.session_state.button_states_chords_tab:
                    st.session_state.button_states_chords_tab[button_key] = {'state': False}
                
                button = st.button(chord, key=button_key, on_click=btn_pressed_callback_chords_tab, args=(button_key,))
            ChordsTabChkBtnStatusAndAssignColour()

    with info_col:
        root = get_root_ctr_key()
        chord_type_1 = get_chordtype_ctr_key()
        if has_active_ctr_and_ctt():
            interval_list = getIntervalList(root, chord_type_1)
            triad_chromatic = getTriadChromatic(root, interval_list)
            print("triad chromatic: ",triad_chromatic)
            st.session_state.chord_list = [] #reset list
            addChord(root, interval_list)
            st.subheader(f"{root}{chord_type_abbr[chord_type.index(chord_type_1)]} ({triad_chromatic[0]} {triad_chromatic[1]} {triad_chromatic[2]})")
            # Get notes in activation order:
            notes = [note+'3' for note in triad_chromatic]
            print("notes:  ",notes)
            figures = []
            fig = draw_music_diagram(notes, clef_image_path)
            figures.append(fig)
            st.pyplot(fig)

    with fretboard_col:
        for i in range(3):
            st.write("")
        figures = []
        if st.session_state.chord_list:
            for displayed_chord in st.session_state.chord_list:
                triad_chromatic = getTriadChromatic(displayed_chord.root_note, displayed_chord.interval)
                highlighted_notes = getHighlightedNotes(triad_chromatic)
                fig = draw_fretboard(show_notes=True, highlighted_notes = highlighted_notes)
                figures.append(fig)

            for i,fig in enumerate(figures):
                st.pyplot(fig)

elif selected == "Scales":
    st.title("Settings")
    st.write("Configure your settings here.")