from langchain_core.prompts import PromptTemplate
from rich.console import Console

from config import llm

console = Console()


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