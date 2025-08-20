from dataclasses import dataclass
from typing import List


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