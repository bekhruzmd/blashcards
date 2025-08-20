import json
import re
from typing import List, Dict
import typer
from langchain_core.prompts import PromptTemplate
from rich.console import Console

from config import llm

console = Console()


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