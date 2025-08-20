import json
import csv
from typing import List, Dict
from pathlib import Path
import pandas as pd
from rich.console import Console

from config import HAS_ANKI

console = Console()


def save_csv(data: List[Dict], path: Path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer"])
        writer.writeheader()
        writer.writerows(data)


def save_json(data: List[Dict], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_xlsx(data: List[Dict], path: Path):
    pd.DataFrame(data).to_excel(path, index=False)


def save_tsv(data: List[Dict], path: Path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer"], delimiter="\t")
        writer.writeheader()
        writer.writerows(data)


def save_md(data: List[Dict], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"### Q: {item['question']}\nA: {item['answer']}\n\n")


def save_txt(data: List[Dict], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"Q: {item['question']}\nA: {item['answer']}\n\n")


def save_apkg(data: List[Dict], path: Path):
    if not HAS_ANKI:
        console.print("[red]genanki not installed. Install with: pip install genanki[/red]")
        return

    try:
        import genanki
        model_def = genanki.Model(
            1607392319, 'FlashcardModel',
            fields=[{'name': 'Question'}, {'name': 'Answer'}],
            templates=[{
                'name': 'Card1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}'
            }],
        )
        deck = genanki.Deck(2059400110, 'Generated Flashcards')
        for item in data:
            deck.add_note(genanki.Note(model=model_def, fields=[item['question'], item['answer']]))
        genanki.Package(deck).write_to_file(path)
    except ImportError:
        console.print("[red]genanki not available for Anki export[/red]")


EXPORT_FUNCTIONS = {
    "csv": save_csv,
    "json": save_json,
    "xlsx": save_xlsx,
    "tsv": save_tsv,
    "md": save_md,
    "txt": save_txt,
    "apkg": save_apkg
}