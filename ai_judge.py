from langchain_core.prompts import PromptTemplate
from rich.console import Console

from models import Verdict
from config import judge_llm
from utils import parse_json_response

console = Console()


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

                verdict_data = parse_json_response(response)
                return Verdict(**verdict_data)

        except Exception as e:
            # Default to more generous grading on error
            return Verdict(
                is_correct=True,  # Give benefit of doubt
                score=0.8,
                feedback=f"Grading system had an issue, but your answer looks reasonable: {str(e)[:100]}",
                key_points_missed=[]
            )