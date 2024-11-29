from PIL import Image, ImageDraw
import streamlit as st
from fretboard import draw_fretboard
from io import BytesIO

st.set_page_config(layout="wide")

# Set up session state for showing the ellipse
if 'show_notes' not in st.session_state:
    st.session_state.show_notes = True  # Initialize state to show the ellipse

# Using containers for vertical organization
intro_container = st.container()
with intro_container:
    st.title("Guitar_0")
    st.write("This application serves as an interactive handbook for anyone trying to learn how to improvise. Pick a scale, a root note and the mode you want to play.")
    st.write("You will see all the possible chords which are allowed. Furthermore you can see possible and commonly used chord progressions")
    st.write("The visual guitar shows you where you have to land your fingers on the fretboard. It is particularly useful for people trying to switch from the piano to the guitar.")

# Layout with left sidebar, main content, and right sidebar
left_sidebar, spacer, image_col1, right_sidebar = st.columns([1,1, 4, 1])  # Adjust the ratio as needed

with left_sidebar:
    st.title("Choose Scale")
    scale_ionian = st.button("Ionian")
    scale_dorian = st.button("Dorian")
    scale_phrygian = st.button("Phrygian")
    scale_lydian = st.button("Lydian")
    scale_myxologidan = st.button("Myxolodian")
    scale_aoelian = st.button("Aoelian")
    scale_locrian = st.button("Locrian")

    if scale_ionian:
        st.write("Iolian Mode")
    elif scale_dorian:
        st.write("Dorian Mode")
    elif scale_phrygian:
        st.write("Phrygian Mode")
    elif scale_lydian:
        st.write("Lydian Mode")
    elif scale_myxologidan:
        st.write("Myxolodian Mode")
    elif scale_aoelian:
        st.write("Aoelian Mode")
    elif scale_locrian:
        st.write("Locrian Mode")

with spacer:
    pass
    #st.title("Choose Key")

with right_sidebar:
    st.title("Right Sidebar")
    button4 = st.button("Show Notes")
    button5 = st.button("Hide Notes")
    button6 = st.button("Button 6")
    if button4:
        st.write("Button 4 was pressed")
        st.session_state.show_notes = True
    elif button5:
        st.write("Button 5 was pressed")
        st.session_state.show_notes = False

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


##################FRETBOARDS#################
a_minor = [[0,1],[2,2],[2,3],[1,4],[0,5]]
fretboard_figures = [
    draw_fretboard(show_notes=st.session_state.show_notes, chord = a_minor),
    draw_fretboard(show_notes=st.session_state.show_notes, chord = a_minor),
    draw_fretboard(show_notes=st.session_state.show_notes, chord = a_minor),
]

def save_plot_as_file(fig, file_format="png"):
    buffer = BytesIO()
    fig.savefig(buffer, format=file_format)
    buffer.seek(0)
    return buffer


with image_col1:
    st.title("1st Fretboard")
    for i, fig in enumerate(fretboard_figures):
        st.pyplot(fig)

"""
        st.download_button(
            label=f"Download Fretboard1 {i + 1} as PDF",
            data=save_plot_as_file(fig, file_format="pdf"),
            file_name=f"fretboard_{i + 1}.pdf",
            mime="application/pdf"
        )
"""


