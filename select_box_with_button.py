import streamlit as st

# Configure the page
st.set_page_config(layout="wide")
st.title("Interactive Button Box")

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

# Create multiple expanders in columns
col1, col2 = st.columns(2)

with col1:
    with st.expander("📁 **Document Actions**", expanded=False):
        if st.button("📄 New Document"):
            st.success("Created a new document!")
        
        if st.button("📂 Open File"):
            st.info("File dialog would open here")
        
        if st.button("💾 Save"):
            st.success("Document saved successfully")
        
        if st.button("🖨️ Print"):
            st.warning("Print dialog would open here")

with col2:
    with st.expander("🎨 **Formatting Options**", expanded=False):
        if st.button("🔠 Change Font"):
            st.info("Font selection dialog")
        
        if st.button("🎨 Color Palette"):
            st.info("Color picker would appear")
        
        if st.button("📏 Adjust Margins"):
            st.info("Margin adjustment controls")
        
        if st.button("🧹 Clear Formatting"):
            st.success("Formatting cleared!")

# Add a status display area
status = st.empty()

# More advanced example with callback functions
def action1():
    status.success("Action 1 executed successfully!")

def action2():
    status.warning("Action 2 requires confirmation")

def action3():
    status.error("Action 3 failed!")

with st.expander("⚙️ **Advanced Settings**", expanded=False):
    st.write("Configure your advanced options:")
    
    if st.button("🛠️ Perform Action 1", on_click=action1):
        pass
    
    if st.button("⚠️ Perform Action 2", on_click=action2):
        pass
    
    if st.button("❌ Perform Action 3", on_click=action3):
        pass
    
    custom_option = st.text_input("Or enter a custom command:")
    if st.button("🚀 Execute Custom Command") and custom_option:
        status.info(f"Executing: {custom_option}")