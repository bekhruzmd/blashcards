import json
from typing import Dict, Any


def parse_json_response(response: str) -> Dict[str, Any]:
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