"""
file_tools.py
--------------
This file contains all the functions the AI Agent uses to safely read
files from ONE folder on your computer. The agent is NOT allowed to
touch anything outside that folder — this is enforced in code below.
"""

import os
from pathlib import Path

from pypdf import PdfReader   # reads PDF files
import docx                   # reads .docx (modern Word) files


# ---------------------------------------------------------------------------
# STEP 1: This is the ONE folder the agent is allowed to look at.
#
# By default it points to a folder called "agent_files" sitting next to
# this script. You can change it in two ways:
#   a) Just drop your PDFs/docs into the "agent_files" folder, OR
#   b) Set an environment variable AGENT_FOLDER to point anywhere you like
#      (instructions for this are in README.md)
# ---------------------------------------------------------------------------
ALLOWED_FOLDER = Path(os.environ.get("AGENT_FOLDER", "./agent_files")).resolve()

# Make sure the folder actually exists so the app doesn't crash on first run.
ALLOWED_FOLDER.mkdir(parents=True, exist_ok=True)

# Which file types we support right now.
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".doc", ".docx"]


def _is_safe_path(target_path: Path) -> bool:
    """
    SECURITY CHECK.
    Makes sure the file the agent wants to open is truly INSIDE the
    allowed folder, and not somewhere else on your computer (e.g. someone
    tricking the agent into reading "../../../passwords.txt").
    """
    try:
        target_path.resolve().relative_to(ALLOWED_FOLDER)
        return True
    except ValueError:
        return False


def list_files() -> list[str]:
    """
    Returns the names of every supported file in the allowed folder.
    The agent calls this first, so it knows what it's allowed to read.
    """
    if not ALLOWED_FOLDER.exists():
        return []
    return sorted(
        f.name for f in ALLOWED_FOLDER.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def read_txt(path: Path) -> str:
    """Reads a plain .txt file and returns its contents as a string."""
    return path.read_text(encoding="utf-8", errors="ignore")


def read_pdf(path: Path) -> str:
    """Reads a .pdf file and pulls the text out of every page."""
    reader = PdfReader(str(path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)


def read_docx(path: Path) -> str:
    """Reads a modern Word (.docx) file and returns all paragraph text."""
    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)


def read_doc(path: Path) -> str:
    """
    Reads an OLD Word (.doc) file.

    .doc is a legacy binary format — Python has no built-in way to read it.
    This function tries to use LibreOffice (a free program) to convert the
    file to text in the background. If LibreOffice isn't installed on your
    computer, it returns a friendly message instead of crashing.
    """
    import subprocess
    import tempfile

    try:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                ["soffice", "--headless", "--convert-to", "txt", "--outdir", tmp, str(path)],
                check=True, capture_output=True, timeout=60
            )
            converted = Path(tmp) / (path.stem + ".txt")
            if converted.exists():
                return converted.read_text(encoding="utf-8", errors="ignore")
            return "[Could not convert this .doc file.]"
    except FileNotFoundError:
        return ("[This .doc file needs LibreOffice installed to be read. "
                 "Easiest fix: open it in Word and 'Save As' .docx instead.]")
    except Exception as e:
        return f"[Error reading .doc file: {e}]"


def read_file(filename: str) -> str:
    """
    MAIN FUNCTION the AI Agent calls.
    Takes a filename (e.g. "notes.pdf") and returns its text content,
    or a clear error message if something's wrong.
    """
    target = (ALLOWED_FOLDER / filename).resolve()

    if not _is_safe_path(target):
        return "Error: Access denied. That file is outside the allowed folder."

    if not target.exists():
        return f"Error: File '{filename}' was not found in the allowed folder."

    suffix = target.suffix.lower()
    if suffix == ".txt":
        return read_txt(target)
    elif suffix == ".pdf":
        return read_pdf(target)
    elif suffix == ".docx":
        return read_docx(target)
    elif suffix == ".doc":
        return read_doc(target)
    else:
        return f"Error: Unsupported file type '{suffix}'."
