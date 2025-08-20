import os
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Local imports
from file_readers import load_text
from flashcard_gen import generate_flashcards
from exporters import EXPORT_FUNCTIONS
from ai_judge import SmartFlashcardJudge
from ai_explainer import SmartExplainer
from models import Attempt
from quiz_logger import save_attempts_log

# Initialize CLI app and console
app = typer.Typer(help="🧠 Smart Flashcards - AI-powered learning system")
console = Console()


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
    console.print(f"[yellow]Run 'python main.py quiz --cards-file {output_file}' to start studying![/yellow]")


@app.command()
def quiz(
        cards_file: str = typer.Option("flashcards.json", "--cards-file", "-c",
                                       help="JSON file containing flashcards"),
        limit: Optional[int] = typer.Option(None, "--limit", "-l",
                                            help="Number of cards to quiz (default: all)"),
        explanations: bool = typer.Option(True, "--explain", "-e",
                                          help="Enable AI explanations for wrong answers"),
        shuffle: bool = typer.Option(True, "--shuffle/--no-shuffle",
                                     help="Shuffle cards before quiz")
):
    """Take an interactive AI-powered quiz with your flashcards."""

    global i
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        console.print("[red]Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON file.[/red]")
        raise typer.Exit(1)

    # Load flashcards
    cards_path = Path(cards_file)
    if not cards_path.exists():
        console.print(f"[red]Cards file not found: {cards_file}[/red]")
        console.print("[yellow]Generate cards first with: python main.py make your_notes.pdf[/yellow]")
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
        f"[bold blue]Smart Flashcards Quiz[/bold blue]\n"
        f"Cards: {len(cards)} | AI Explanations: {'[green]YES[/green]' if explanations else '[red]NO[/red]'}\n"
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
            console.print("[yellow]Quiz ended by user[/yellow]")
            break
        elif user_answer.lower() == 'skip':
            console.print("[yellow]⭐️ Skipped[/yellow]")
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

    # Final results - show even if quit early
    if attempts:
        log_file = save_attempts_log(attempts)
        accuracy = (correct_count / len(attempts)) * 100

        # Results panel
        status = "Quiz Complete!" if i >= len(cards) else f"Quiz Ended Early (answered {len(attempts)}/{len(cards)})"
        results_text = (
            f"[bold]{status}[/bold]\n"
            f"Score: {correct_count}/{len(attempts)} ({accuracy:.1f}%)\n"
            f"Attempts saved to: {log_file}"
        )
        console.print(Panel(results_text, title="📊 Results", border_style="green"))
    else:
        console.print("[yellow]No questions answered - no results to save.[/yellow]")


@app.command()
def review(
        attempts_dir: str = typer.Option("quiz_attempts", "--dir", "-d",
                                         help="Directory containing quiz attempt files"),
        session_file: Optional[str] = typer.Option(None, "--file", "-f",
                                                   help="Specific session file to review")
):
    """Review your quiz performance and statistics."""

    attempts_path = Path(attempts_dir)
    if not attempts_path.exists():
        console.print(f"[red]No attempts directory found: {attempts_dir}[/red]")
        console.print("[yellow]Take a quiz first to generate performance data.[/yellow]")
        raise typer.Exit(1)

    # Load attempts from all files in directory or specific file
    attempts = []

    if session_file:
        # Review specific session file
        file_path = attempts_path / session_file
        if not file_path.exists():
            console.print(f"[red]Session file not found: {file_path}[/red]")
            raise typer.Exit(1)
        files_to_process = [file_path]
    else:
        # Review all .jsonl files in directory
        files_to_process = list(attempts_path.glob("*.jsonl"))
        if not files_to_process:
            console.print(f"[yellow]No quiz session files found in {attempts_dir}[/yellow]")
            return

    # Load all attempts
    for file_path in files_to_process:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        attempts.append(json.loads(line))
        except Exception as e:
            console.print(f"[yellow]Error reading {file_path}: {e}[/yellow]")

    if not attempts:
        console.print("[yellow]No quiz attempts found.[/yellow]")
        return

    # Show which files were processed
    if len(files_to_process) > 1:
        console.print(f"[blue]Analyzing {len(attempts)} attempts from {len(files_to_process)} sessions[/blue]\n")
    else:
        console.print(f"[blue]Analyzing {len(attempts)} attempts from: {files_to_process[0].name}[/blue]\n")

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