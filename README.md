# AI File Reading Agent

A simple AI agent built with **Python**, **Streamlit**, and the **Google Gemini API**. It reads files from one approved local folder and answers questions about their contents.

## Features

- Browser-based chat interface
- Reads PDF, TXT, DOCX, and DOC files
- Uses Gemini function calling
- Restricts access to one local folder
- Keeps temporary chat history

## Setup

Create a Folder in the same location as the other files and name it "agent_files" and store the Files you want the AI Agent to read

Create a virtual environment:

powershell
py -m venv .venv


Install the requirements:

powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt


Create a `.env` file: Use the `env.example`  file

Place your documents inside the `agent_files` folder.

## Run

Click the `run.bat` file

or

Open powershell and type

.\.venv\Scripts\python.exe -m streamlit run agent.py --server.port 8501


Open in the Browser:

http://localhost:8501


## Supported Files

- `.pdf`
- `.txt`
- `.docx`
- `.doc`


