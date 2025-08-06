import os
from google.cloud import aiplatform  # comes with the VertexAI lib

# explicitly point to your service account (if you haven’t already)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bekhruzmd/Desktop/flash-gen/service_account.json"

# initialize Vertex AI SDK with your project and region
aiplatform.init(
    project="tribal-cortex-468019-h1",
    location="us-central1"        # or your preferred region
)

import argparse
import csv
import json
import pandas as pd

# File readers
import pdfplumber
from PyPDF2 import PdfReader
import docx

# LLM & Vertex AI
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
llm = VertexAI(
    model_name="gemini-2.5-flash",
    temperature=0.3,
    # you can also pass project & location here if you like:
    project="tribal-cortex-468019-h1",
    location="us-central1",
)


# Optional Anki export
try:
    import genanki
    HAS_ANKI = True
except ImportError:
    HAS_ANKI = False


def load_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".pdf":
        # Try pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except Exception as e:
            print(f"⚠️ pdfplumber failed: {e}, falling back to PyPDF2…")

        # Fallback PyPDF2
        try:
            reader = PdfReader(file_path)
            return "".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            raise RuntimeError(f"Cannot read PDF content: {e}") from e

    elif ext == ".docx":
        try:
            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            raise RuntimeError(f"Cannot read DOCX content: {e}") from e

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def generate_flashcards(text: str, model: VertexAI) -> list[dict]:
    prompt = PromptTemplate.from_template("""
Convert the following study notes into flashcards.
Each flashcard should be an object with "question" and "answer".

Return ONLY a JSON array of these objects. Do NOT wrap it in any extra text.

Notes:
{text}
""")
    # chain prompt → model, get raw string
    chain = prompt | model
    raw = chain.invoke({"text": text})

    # parse JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON from Gemini:\n{raw}")


def save_csv(data, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["question", "answer"])
        w.writeheader(); w.writerows(data)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_xlsx(data, path):
    pd.DataFrame(data).to_excel(path, index=False)


def save_tsv(data, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["question","answer"], delimiter="\t")
        w.writeheader(); w.writerows(data)


def save_md(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for itm in data:
            f.write(f"### Q: {itm['question']}\nA: {itm['answer']}\n\n")


def save_txt(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for itm in data:
            f.write(f"Q: {itm['question']}\nA: {itm['answer']}\n\n")


def save_apkg(data, path):
    if not HAS_ANKI:
        print("❌ genanki not installed; `pip install genanki` to enable Anki export")
        return
    model_def = genanki.Model(
        1607392319, 'FlashcardModel',
        fields=[{'name': 'Question'},{'name':'Answer'}],
        templates=[{
            'name':'Card1',
            'qfmt':'{{Question}}',
            'afmt':'{{FrontSide}}<hr id="answer">{{Answer}}'
        }],
    )
    deck = genanki.Deck(2059400110, 'Generated Flashcards')
    for itm in data:
        deck.add_note(genanki.Note(model=model_def, fields=[itm['question'], itm['answer']]))
    genanki.Package(deck).write_to_file(path)


def save_output(data, fmt, path):
    {
        "csv":  save_csv,
        "json": save_json,
        "xlsx": save_xlsx,
        "tsv":  save_tsv,
        "md":   save_md,
        "txt":  save_txt,
        "apkg": save_apkg
    }[fmt](data, path)


def main():
    p = argparse.ArgumentParser(description="Notes → Flashcards with Gemini")
    p.add_argument("-o","--output",
                   choices=["csv","json","xlsx","tsv","md","txt","apkg"],
                   default="csv", help="Export format")
    p.add_argument("input_file", nargs="?", help="Path to .txt/.pdf/.docx notes")
    args = p.parse_args()

    if not args.input_file:
        args.input_file = input("📁 Path to your notes file: ").strip()

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ Set GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON.")
        exit(1)

    notes = load_text(args.input_file)
    llm  = VertexAI(model_name="gemini-2.5-flash", temperature=0.3)
    cards = generate_flashcards(notes, llm)

    out = f"output_flashcards.{args.output}"
    print(f"💾 Saving → {out}")
    save_output(cards, args.output, out)
    print("✅ Done!")


if __name__ == "__main__":
    main()
