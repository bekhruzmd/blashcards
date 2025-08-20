from pathlib import Path
import typer
from rich.console import Console

import pdfplumber
from PyPDF2 import PdfReader
import docx

console = Console()


def load_text(file_path: str) -> str:
    """Load text content from various file formats."""
    path_obj = Path(file_path)
    ext = path_obj.suffix.lower()

    if ext == ".txt":
        return path_obj.read_text(encoding="utf-8")

    elif ext == ".pdf":
        try:
            with pdfplumber.open(str(path_obj)) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except Exception as e:
            console.print(f"[yellow]pdfplumber failed: {e}, trying PyPDF2...[/yellow]")

        try:
            reader = PdfReader(str(path_obj))
            return "".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            console.print(f"[red]Cannot read PDF content: {e}[/red]")
            raise typer.Exit(code=1)

    elif ext == ".docx":
        try:
            doc = docx.Document(str(path_obj))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            console.print(f"[red]Cannot read DOCX content: {e}[/red]")
            raise typer.Exit(code=1)

    else:
        console.print(f"[red]Unsupported file type: {ext}[/red]")
        raise typer.Exit(code=1)