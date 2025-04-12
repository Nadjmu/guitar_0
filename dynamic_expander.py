import streamlit as st

# Initialize session state
if 'expander_label' not in st.session_state:
    st.session_state.expander_label = "Choose an option"

# Display the expander (label updates dynamically)
with st.expander(st.session_state.expander_label):
    # Buttons update the label instantly
    if st.button("Option 1"):
        st.session_state.expander_label = "Option 1"
        st.rerun()  # Force immediate update
    
    if st.button("Option 2"):
        st.session_state.expander_label = "Option 2"
        st.rerun()
    
    if st.button("Option 3"):
        st.session_state.expander_label = "Option 3"
        st.rerun()