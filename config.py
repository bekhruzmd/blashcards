import os
from google.cloud import aiplatform
from langchain_google_vertexai import VertexAI

# Google Cloud setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bekhruzmd/Desktop/flash-gen/service_account.json"
aiplatform.init(
    project="tribal-cortex-468019-h1",
    location="us-central1"
)

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

# Check for optional dependencies
try:
    import genanki
    HAS_ANKI = True
except ImportError:
    HAS_ANKI = False