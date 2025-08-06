# Flashcard Generator (Draft)

> ⚠️ **Note:** This is a draft version and not the final release. Features and usage may change.

A simple CLI tool that converts your study notes (`.txt`, `.pdf`, or `.docx`) into flashcards using Google’s Gemini model (via Vertex AI). Exports to CSV, JSON, XLSX, TSV, Markdown, plain-text, or Anki (`.apkg`).

## Features

* **Input formats:** `.txt`, `.pdf`, `.docx`
* **Output formats:** `csv`, `json`, `xlsx`, `tsv`, `md`, `txt`, `apkg`
* **AI core:** Google Gemini (Vertex AI) via `langchain-google-vertexai`
* **Anki support:** optional via `genanki`

## Prerequisites

* Python 3.8+
* A Google Cloud project with Vertex AI enabled
* A service-account JSON key (set in `GOOGLE_APPLICATION_CREDENTIALS`)
* (Optional) `GEMINI_API_KEY` for MakerSuite endpoints

## Installation

```bash
# Clone the repo
git clone git@github.com:<you>/flashcard-generator.git
cd flashcard-generator

# Create & activate a virtualenv
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate.bat    # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. **Service Account**

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/full/path/to/gemini-key.json"
   ```

2. **(Optional) MakerSuite API Key**

   ```bash
   export GEMINI_API_KEY="your-maker-suite-key"
   ```

## Usage

```bash
# Run interactively (you’ll be prompted for your notes file & format)
python generator.py

# Or specify input and format on the command line
python generator.py -o json path/to/lecture_notes.pdf
```

Outputs a file named `output_flashcards.{format}` in the current directory.

## .gitignore

Be sure your `.gitignore` includes:

```
venv/
.env
gemini_key.json
output_flashcards.*
```

---

*This README is a work-in-progress and may be updated.*
