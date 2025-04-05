import streamlit as st

# Main directory: "Diatonic Scales"
st.title("Diatonic Scales")

if "show_modes" not in st.session_state:
    st.session_state["show_modes"] = False

# Button to toggle modes view
if st.button("Diatonic Scales"):
    st.session_state["show_modes"] = not st.session_state["show_modes"]

# Display the modes in a vertical directory-like structure
if st.session_state["show_modes"]:
    st.subheader("Modes of the Diatonic Scale")
    modes = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]

    # Create vertical buttons for each mode
    for mode in modes:
        if st.button(mode):
            st.write(f"You selected the {mode} mode!")
