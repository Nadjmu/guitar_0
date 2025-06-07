## loading all the environment variables
from dotenv import load_dotenv
load_dotenv() 

import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("API_KEY"))

## function to load Gemini Pro model and get repsonses
model=genai.GenerativeModel("gemini-2.0-flash") 
chat = model.start_chat(history=[])
def get_gemini_response(question):
    
    response=chat.send_message(question,stream=True)
    return response

##initialize our streamlit app

st.set_page_config(page_title="Q&A Demo")

st.header("Gemini LLM Application")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

input=st.text_input("Input: ",key="input")
submit=st.button("Ask the question")

st.markdown("""
<style>
    .stMarkdown {
        white-space: pre-wrap;  /* Preserves formatting & prevents line breaks */
        word-break: break-word; /* Ensures long words don't overflow */
    }
</style>
""", unsafe_allow_html=True)

if submit and input:
    response = get_gemini_response(input)
    full_response = "".join(chunk.text for chunk in response)
    st.markdown(f"```\n{full_response}\n```")  # Displays in a code block but wraps text

