import streamlit as st
import streamlit.components.v1 as components
from music_theory import chromatic_scale, all_notes
from music_diagram import draw_music_diagram

# Initialize session state
if "button_states" not in st.session_state:
    st.session_state.button_states = {}#[False]*len(all_notes)

unpressed_colour = "#FFFFFF"  # White
pressed_colour = "#B0B0B0"    # Grey


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
    for i in range(len(all_notes)):
        ChangeButtonColour(all_notes[i], st.session_state.button_states[all_notes[i]])

def btn_pressed_callback(button_key):
    st.session_state.button_states[button_key] = not st.session_state.button_states[button_key]

for i in range(12):
    row_cols = st.columns([1.8, 1.8, 10, 10])
    for j in range(3):
        with row_cols[j]:
            note = chromatic_scale[(4 + i) % 12]
            button_key = f"{note}{j+2}"
                
            # Initialize state if not exists
            if button_key not in st.session_state.button_states:
                st.session_state.button_states[button_key] = False
                
            # Create button with dynamic class
            button = st.button(button_key, key=button_key,help=button_key, on_click=btn_pressed_callback, args=(button_key,))
                
ChkBtnStatusAndAssignColour()
