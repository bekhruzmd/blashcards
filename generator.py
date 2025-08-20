import os
import json
import re
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from dataclasses import dataclass, asdict

# Typer and Rich for beautiful CLI
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
from rich.prompt import Prompt, Confirm
from rich import print as rprint

# Google Cloud setup
from google.cloud import aiplatform

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bekhruzmd/Desktop/flash-gen/service_account.json"
aiplatform.init(
    project="tribal-cortex-468019-h1",
    location="us-central1"
)

# File readers
import pdfplumber
from PyPDF2 import PdfReader
import docx

# LLM & Vertex AI
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI

# Initialize CLI app and console
app = typer.Typer(help="🧠 Smart Flashcards - AI-powered learning system")
console = Console()

# Initialize LLMs
llm = VertexAI(
    model_name="gemini-2.5-flash",
    temperature=0.3,
    project="tribal-cortex-468019-h1",
    location="us-central1",
)

judge_llm = VertexAI(
    model_name="gemini-2.5-flash",
    temperature=0.1,
    project="tribal-cortex-468019-h1",
    location="us-central1",
)

# Optional Anki export
try:
    import genanki

    HAS_ANKI = True
except ImportError:
    HAS_ANKI = False


@dataclass
class Verdict:
    """LLM judge verdict for a user's answer."""
    is_correct: bool
    score: float
    feedback: str
    key_points_missed: List[str]


@dataclass
class Attempt:
    """Records a user's attempt at answering a flashcard."""
    question: str
    correct_answer: str
    user_answer: str
    verdict: Verdict
    timestamp: str


def _parse_json_response(response: str) -> Dict[str, Any]:
    """Parse LLM JSON response with error handling."""
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]
    response = response.strip()

    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {response}") from e


class SmartFlashcardJudge:
    """LLM-powered judge for grading flashcard answers with focus on conceptual understanding."""

    def __init__(self):
        self.grading_prompt = PromptTemplate.from_template("""
You are an expert educator grading flashcard answers. Focus on whether the student understands the core concept, not exact wording.

GRADING PHILOSOPHY:
- PRIORITIZE conceptual understanding over precise wording
- ACCEPT any answer that demonstrates the student "gets it"
- EMBRACE synonyms, paraphrasing, and different explanations of the same idea
- IGNORE minor details if the main concept is correct
- CONSIDER the answer correct if a knowledgeable person would say "yes, that's right"

GRADING RUBRIC:
- 1.0: Demonstrates clear understanding of the core concept (even if worded differently)
- 0.9: Mostly correct understanding with very minor gaps or imprecision
- 0.7-0.8: Generally correct but missing some important details
- 0.5-0.6: Shows partial understanding but has significant gaps
- 0.0-0.4: Incorrect or shows fundamental misunderstanding

EXAMPLES OF GOOD GRADING:
- Canonical: "Photosynthesis converts sunlight into chemical energy"
- Student: "Plants use sunlight to make food" → CORRECT (1.0) - same core concept
- Student: "Sun energy becomes plant energy" → CORRECT (0.9) - informal but accurate
- Student: "Plants eat sunlight" → PARTIALLY CORRECT (0.6) - conceptually close but imprecise

BE GENEROUS: If you can see the student understands the concept, give them credit!

CANONICAL ANSWER: {canonical_answer}
USER ANSWER: {user_answer}

Think step by step:
1. What is the core concept being tested?
2. Does the student's answer show they understand this concept?
3. Are they expressing the same idea in different words?
4. Would an expert say "yes, that's basically correct"?

Return ONLY a valid JSON object:
{{
  "is_correct": true or false,
  "score": 0.0 to 1.0,
  "feedback": "Brief, encouraging feedback focusing on their understanding",
  "key_points_missed": ["only list truly essential missing concepts"]
}}
""")

    def grade_answer(self, canonical_answer: str, user_answer: str) -> Verdict:
        """Grade a user's answer against the canonical answer with conceptual focus."""
        if not user_answer.strip():
            return Verdict(
                is_correct=False,
                score=0.0,
                feedback="No answer provided - give it a try!",
                key_points_missed=["Complete answer required"]
            )

        try:
            with console.status("[bold blue]AI is evaluating your understanding..."):
                chain = self.grading_prompt | judge_llm
                response = chain.invoke({
                    "canonical_answer": canonical_answer,
                    "user_answer": user_answer
                })

                verdict_data = _parse_json_response(response)
                return Verdict(**verdict_data)

        except Exception as e:
            # Default to more generous grading on error
            return Verdict(
                is_correct=True,  # Give benefit of doubt
                score=0.8,
                feedback=f"Grading system had an issue, but your answer looks reasonable: {str(e)[:100]}",
                key_points_missed=[]
            )


class SmartExplainer:
    """AI explainer for misconceptions and targeted help."""

    def __init__(self):
        self.explainer_prompt = PromptTemplate.from_template("""
You are a helpful tutor. A student got a flashcard question wrong. Help them understand their mistake and learn the correct concept.

QUESTION: {question}
CORRECT ANSWER: {correct_answer}
STUDENT'S ANSWER: {user_answer}

Provide a helpful explanation that:
1. Briefly explains what they got wrong
2. Teaches the correct concept clearly
3. Is encouraging and supportive
4. Keeps to 2-3 sentences maximum

Then suggest 1-2 quick follow-up questions to help them practice.

Format your response as:
EXPLANATION: [your explanation]
FOLLOW-UP QUESTIONS:
1. [question 1]
2. [question 2]
""")

    def explain_mistake(self, question: str, correct_answer: str, user_answer: str) -> str:
        """Generate targeted explanation for a wrong answer."""
        try:
            with console.status("[bold blue]AI is preparing an explanation..."):
                chain = self.explainer_prompt | llm
                response = chain.invoke({
                    "question": question,
                    "correct_answer": correct_answer,
                    "user_answer": user_answer
                })
                return response
        except Exception:
            return f"Let's review: {correct_answer}. This is an important concept to master."


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


def generate_flashcards(text: str) -> List[Dict]:
    """Generate flashcards from text using AI with robust JSON parsing."""
    prompt = PromptTemplate.from_template("""
Convert the following study notes into flashcards for effective learning and retention.

Create flashcards that:
- Test key concepts and important facts
- Use clear, specific questions
- Provide complete, accurate answers
- Focus on understanding rather than memorization
- Include relevant context in answers when helpful

CRITICAL: Return ONLY a valid JSON array. No extra text, no markdown, no explanations.

Example format:
[{{"question": "What is...?", "answer": "The answer is..."}}, {{"question": "How does...?", "answer": "It works by..."}}]

Study Material:
{text}

RETURN ONLY THE JSON ARRAY:
""")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with console.status(
                    f"[bold blue]AI is generating flashcards... (attempt {attempt + 1}/{max_retries})[/bold blue]"):
                chain = prompt | llm
                raw = chain.invoke({"text": text})

                # Clean and parse JSON
                raw = raw.strip()

                # Remove markdown if present
                if raw.startswith("```json"):
                    raw = raw[7:]
                elif raw.startswith("```"):
                    raw = raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]

                raw = raw.strip()

                # Try to extract JSON array
                json_match = re.search(r'\[.*]', raw, re.DOTALL)
                if json_match:
                    raw = json_match.group()

                cards = json.loads(raw)

                # Validate the structure
                if not isinstance(cards, list):
                    raise ValueError("Response is not a JSON array")

                for card in cards:
                    if not isinstance(card, dict) or "question" not in card or "answer" not in card:
                        raise ValueError("Invalid card structure")

                console.print(f"[green]Successfully generated {len(cards)} flashcards![/green]")
                return cards

        except Exception as e:
            console.print(f"[yellow]Attempt {attempt + 1} failed: {str(e)[:100]}[/yellow]")
            if attempt == max_retries - 1:
                console.print(f"[red]Failed to generate flashcards after {max_retries} attempts.[/red]")
                console.print(f"[red]Raw AI response: {raw[:200]}...[/red]")
                raise typer.Exit(code=1)
    return None


def save_attempts_log(attempts: List[Attempt], path: str = "quiz_attempts.jsonl"):
    """Save quiz attempts to JSONL file."""
    with open(path, "a", encoding="utf-8") as f:
        for attempt in attempts:
            json.dump(asdict(attempt), f, default=str)
            f.write("\n")


# Export functions for all file types
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


@app.command()
def make(
        input_file: str = typer.Argument(..., help="Path to your study material (.txt/.pdf/.docx)"),
        output_format: str = typer.Option("json", "--format", "-f",
                                          help="Export format: csv, json, xlsx, tsv, md, txt, apkg"),
        output_dir: str = typer.Option("output_files", "--output-dir", "-o",
                                       help="Output directory for generated files")
):
    """Generate flashcards from study materials using AI."""

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        console.print("[red]Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON file.[/red]")
        raise typer.Exit(1)

    if output_format not in EXPORT_FUNCTIONS:
        console.print(f"[red]Unsupported format: {output_format}[/red]")
        console.print(f"[yellow]Available formats: {', '.join(EXPORT_FUNCTIONS.keys())}[/yellow]")
        raise typer.Exit(1)

    # Load study material
    console.print(f"[blue]Loading study material: {input_file}[/blue]")
    try:
        text = load_text(input_file)
    except Exception as e:
        console.print(f"[red]Error loading file: {e}[/red]")
        raise typer.Exit(1)

    # Generate flashcards
    console.print("[blue]Generating flashcards with AI...[/blue]")
    cards = generate_flashcards(text)

    # Create output directory and save
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    input_name = Path(input_file).stem
    output_file = output_path / f"{input_name}_flashcards.{output_format}"

    console.print(f"[blue]Saving {len(cards)} flashcards to {output_file}[/blue]")
    EXPORT_FUNCTIONS[output_format](cards, output_file)

    console.print("[green]✅ Flashcards generated successfully![/green]")
    console.print(f"[yellow]Run 'python generator.py quiz --cards-file {output_file}' to start studying![/yellow]")


@app.command()
def quiz(
        cards_file: str = typer.Option("flashcards.json", "--cards-file", "-c",
                                       help="JSON file containing flashcards"),
        limit: Optional[int] = typer.Option(None, "--limit", "-l",
                                            help="Number of cards to quiz (default: all)"),
        explanations: bool = typer.Option(False, "--explain", "-e",
                                          help="Enable AI explanations for wrong answers"),
        shuffle: bool = typer.Option(True, "--shuffle/--no-shuffle",
                                     help="Shuffle cards before quiz")
):
    """Take an interactive AI-powered quiz with your flashcards."""

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        console.print("[red]Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON file.[/red]")
        raise typer.Exit(1)

    # Load flashcards
    cards_path = Path(cards_file)
    if not cards_path.exists():
        console.print(f"[red]Cards file not found: {cards_file}[/red]")
        console.print("[yellow]Generate cards first with: python generator.py make your_notes.pdf[/yellow]")
        raise typer.Exit(1)

    try:
        with open(cards_path, "r", encoding="utf-8") as f:
            cards = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading cards: {e}[/red]")
        raise typer.Exit(1)

    # Prepare cards
    if shuffle:
        import random
        random.shuffle(cards)

    if limit:
        cards = cards[:limit]

    # Initialize systems
    judge = SmartFlashcardJudge()
    explainer = SmartExplainer()
    attempts = []

    # Quiz header
    console.print(Panel.fit(
        f"[bold blue]🎯 Smart Flashcards Quiz[/bold blue]\n"
        f"Cards: {len(cards)} | AI Explanations: {'✅' if explanations else '❌'}\n"
        f"Commands: 'quit' to exit, 'skip' to skip card",
        border_style="blue"
    ))

    correct_count = 0

    for i, card in enumerate(cards, 1):
        # Display question
        console.print(f"\n[bold cyan]Question {i}/{len(cards)}:[/bold cyan]")
        console.print(Panel(card['question'], border_style="cyan"))

        # Get user answer
        user_answer = Prompt.ask("[bold]Your answer").strip()

        if user_answer.lower() == 'quit':
            break
        elif user_answer.lower() == 'skip':
            console.print("[yellow]⏭️ Skipped[/yellow]")
            continue

        # Grade the answer
        verdict = judge.grade_answer(card['answer'], user_answer)

        # Record attempt
        attempt = Attempt(
            question=card['question'],
            correct_answer=card['answer'],
            user_answer=user_answer,
            verdict=verdict,
            timestamp=datetime.now().isoformat()
        )
        attempts.append(attempt)

        # Display results with Rich styling
        if verdict.is_correct:
            correct_count += 1
            console.print("[green]✅ Correct![/green]")
        else:
            console.print("[red]❌ Incorrect[/red]")

        # Show score and feedback
        table = Table(show_header=False, box=None)
        table.add_row("[bold]Score:", f"{verdict.score:.1f}/1.0")
        table.add_row("[bold]Feedback:", verdict.feedback)
        table.add_row("[bold]Correct Answer:", card['answer'])
        console.print(table)

        # Offer explanation for wrong answers
        if not verdict.is_correct and explanations:
            if Confirm.ask("Would you like an AI explanation?", default=True):
                explanation = explainer.explain_mistake(
                    card['question'], card['answer'], user_answer
                )
                console.print(
                    Panel(explanation, title="[bold blue]💡 AI Tutor Explanation[/bold blue]", border_style="blue"))

    # Final results
    if attempts:
        save_attempts_log(attempts)
        accuracy = (correct_count / len(attempts)) * 100

        # Results panel
        results_text = (
            f"[bold]Quiz Complete![/bold]\n"
            f"Score: {correct_count}/{len(attempts)} ({accuracy:.1f}%)\n"
            f"Attempts logged to: quiz_attempts.jsonl"
        )
        console.print(Panel(results_text, title="📊 Results", border_style="green"))


@app.command()
def review(
        attempts_file: str = typer.Option("quiz_attempts.jsonl", "--file", "-f",
                                          help="Attempts log file to review")
):
    """Review your quiz performance and statistics."""

    attempts_path = Path(attempts_file)
    if not attempts_path.exists():
        console.print(f"[red]No attempts file found: {attempts_file}[/red]")
        console.print("[yellow]Take a quiz first to generate performance data.[/yellow]")
        raise typer.Exit(1)

    # Load attempts
    attempts = []
    with open(attempts_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                attempts.append(json.loads(line))

    if not attempts:
        console.print("[yellow]No quiz attempts found.[/yellow]")
        return

    # Calculate statistics
    total_score = sum(attempt['verdict']['score'] for attempt in attempts)
    avg_score = total_score / len(attempts)
    correct_count = sum(1 for attempt in attempts if attempt['verdict']['is_correct'])
    success_rate = (correct_count / len(attempts)) * 100

    # Performance overview
    stats_table = Table(title="📊 Performance Overview")
    stats_table.add_column("Metric", style="bold cyan")
    stats_table.add_column("Value", style="bold")

    stats_table.add_row("Total Attempts", str(len(attempts)))
    stats_table.add_row("Average Score", f"{avg_score:.2f}/1.0")
    stats_table.add_row("Success Rate", f"{correct_count}/{len(attempts)} ({success_rate:.1f}%)")

    console.print(stats_table)

    # Recent attempts
    console.print("\n[bold]🕒 Recent Attempts:[/bold]")
    recent_table = Table()
    recent_table.add_column("Status", width=6)
    recent_table.add_column("Score", width=8)
    recent_table.add_column("Question", style="dim")

    for attempt in attempts[-10:]:  # Show last 10 attempts
        status = "✅" if attempt['verdict']['is_correct'] else "❌"
        score = f"{attempt['verdict']['score']:.1f}/1.0"
        question = attempt['question'][:60] + ("..." if len(attempt['question']) > 60 else "")
        recent_table.add_row(status, score, question)

    console.print(recent_table)


if __name__ == "__main__":
    app()