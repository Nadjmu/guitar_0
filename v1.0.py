import streamlit as st
import streamlit.components.v1 as components
from music_theory import chromatic_scale, all_notes, string_notes
from music_diagram import draw_music_diagram
from fretboard import draw_fretboard

st.set_page_config(layout="wide")  # Must be the first Streamlit command
# Initialize session state
if "button_states" not in st.session_state:
    st.session_state.button_states = {} # {button_key: {'state': False, 'order': None}}

if 'button_press_order' not in st.session_state:
    st.session_state.button_press_order = []  # Tracks the sequence of pressed buttons

unpressed_colour = "#FFFFFF"  # White
pressed_colour = "#B0B0B0"    # Grey

clef_image_path = "clef.png"  # Path to uploaded clef image

fretboard_ids = {}
current_id = 1  # Start counting at 1

##initialize fretboard ids ###
for string in range(6):  # Process strings in order (0-5)
    for fret in range(13):  # Process frets in order (0-12)
        base_ids = [1,6,11,16,20,25]
        current_id = base_ids[string]+fret
        
        # Assign new ID (never reuse, even for same note in different octaves)
        fretboard_ids[(fret, string)] = current_id


def ChangeButtonColour(widget_label, prsd_status):
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

def ChkBtnStatusAndAssignColour():
    list_notes_key = list(all_notes.keys())
    for i in range(len(list_notes_key)):
        #print(list(all_notes.keys()))
        ChangeButtonColour(list_notes_key[i], st.session_state.button_states[list_notes_key[i]]['state'])

def btn_pressed_callback(button_key):
    # Toggle state
    current_state = st.session_state.button_states[button_key]['state']
    st.session_state.button_states[button_key]['state'] = not current_state
    # Update press order if being activated
    if not current_state:  # If was False and now True (being activated)
        st.session_state.button_states[button_key]['order'] = len(st.session_state.button_press_order)
        st.session_state.button_press_order.append(button_key)
    else:  # If being deactivated
        if button_key in st.session_state.button_press_order:
            st.session_state.button_press_order.remove(button_key)

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

intro_container = st.container()
with intro_container:
    st.title("🪕 Guitar_0")
    st.write("This application serves as an interactive handbook for anyone trying to learn how to improvise. Pick a scale, a root note and the mode you want to play.")
    st.write("You will see all the possible chords which are allowed. Furthermore you can see possible and commonly used chord progressions")
    st.write("The visual guitar shows you where you have to land your fingers on the fretboard. It is particularly useful for people trying to switch from the piano to the guitar.\n \n")


key_1_col, key_2_col, key_3_col, music_diagram_col, fretboard_col = st.columns([1,1,1,8,13])
for i in range(12):
    for j in range(3):
        note = chromatic_scale[(4 + i) % 12]
        new_octave = (4+i)//12
        button_key = f"{note}{j+new_octave+2}"
        # Initialize state if not exists
        if button_key not in st.session_state.button_states:
            st.session_state.button_states[button_key] = {'state': False, 'order': None}
        if j==0:
            with key_1_col:
                # Create button with dynamic class
                button = st.button(button_key, key=button_key, on_click=btn_pressed_callback, args=(button_key,))
        elif j==1:
            with key_2_col:
                # Create button with dynamic class
                button = st.button(button_key, key=button_key, on_click=btn_pressed_callback, args=(button_key,))
        elif j==2:
            with key_3_col:
                # Create button with dynamic class
                button = st.button(button_key, key=button_key, on_click=btn_pressed_callback, args=(button_key,))
ChkBtnStatusAndAssignColour()



with music_diagram_col:
    with st.container():
        for i in range(12):
            st.write("")

        # Get notes in activation order:
        notes = [key for key in st.session_state.button_press_order if st.session_state.button_states[key]['state'] is True]
        figures = []
        fig = draw_music_diagram(notes, clef_image_path)
        figures.append(fig)
        st.pyplot(fig)

with fretboard_col:
    with st.container():
        for i in range(15):
            st.write("")

        coordinates_notes = keyToCoordinates(notes)
        figures = []
        fig = draw_fretboard(True, coordinates_notes)
        figures.append(fig)
        st.pyplot(fig)
