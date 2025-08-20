import json
from typing import List
from dataclasses import asdict
from pathlib import Path
from datetime import datetime

from models import Attempt


def save_attempts_log(attempts: List[Attempt], attempts_dir: str = "quiz_attempts"):
    """Save quiz attempts to JSONL file in dedicated directory."""
    # Create the quiz_attempts directory if it doesn't exist
    attempts_path = Path(attempts_dir)
    attempts_path.mkdir(exist_ok=True)

    # Create filename with timestamp for this session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quiz_session_{timestamp}.jsonl"
    file_path = attempts_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        for attempt in attempts:
            json.dump(asdict(attempt), f, default=str)
            f.write("\n")

    return str(file_path)