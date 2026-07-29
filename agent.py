"""
agent.py
--------
A basic browser-based Gemini file-reading agent built with Streamlit.

The agent can:
  1. List readable files in one allowed folder.
  2. Read a selected PDF, TXT, DOC, or DOCX file.
  3. Use the file contents to answer questions.

Run with:
    streamlit run agent.py
"""

import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from file_tools import ALLOWED_FOLDER, list_files, read_file


# Load variables from a local .env file when present.
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
MAX_HISTORY_MESSAGES = 20

SYSTEM_INSTRUCTION = (
    "You are a helpful file-reading assistant. You can only inspect files by "
    "using the provided list_files and read_file tools. Before answering a "
    "question about the user's documents, use the tools to inspect the real "
    "files and relevant content. Never invent file contents. If a requested "
    "file is missing or unreadable, explain that clearly. Be concise and clear."
)


def get_client() -> genai.Client:
    """Create the Gemini client using GEMINI_API_KEY from the environment."""
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file and restart the app."
        )
    return genai.Client(api_key=API_KEY)


def build_contents(chat_history: list[dict], user_message: str) -> list[types.Content]:
    """Convert the Streamlit chat history into Gemini content objects."""
    recent_history = chat_history[-MAX_HISTORY_MESSAGES:]
    contents: list[types.Content] = []

    for message in recent_history:
        role = "model" if message["role"] == "assistant" else "user"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=message["content"])],
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )
    return contents


def run_agent(user_message: str, chat_history: list[dict]) -> str:
    """
    Send the conversation to Gemini.

    The Google Gen AI SDK automatically handles function calling when Python
    functions are passed as tools: Gemini selects a tool, the SDK runs it,
    returns the tool result to Gemini, and produces the final text response.
    """
    client = get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=build_contents(chat_history, user_message),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[list_files, read_file],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=6
            ),
            max_output_tokens=1500,
        ),
    )

    if not response.text:
        return "Gemini returned no text response. Please try again."
    return response.text


# ---------------------------------------------------------------------------
# Streamlit browser UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AI File Agent", page_icon="📁")
st.title("📁 AI File Reading Agent")
st.caption(f"Model: {MODEL} | Allowed folder: {ALLOWED_FOLDER}")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Files in your folder")
    files = list_files()
    if files:
        for filename in files:
            st.write("📄", filename)
    else:
        st.info(
            "No supported files found. Add .pdf, .txt, .doc, or .docx files "
            "to the allowed folder."
        )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask something about your files...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("AI Agent is checking your files..."):
            try:
                answer = run_agent(user_input, st.session_state.messages[:-1])
            except Exception as exc:
                answer = f"Error: {exc}"
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
