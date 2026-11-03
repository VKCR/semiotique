import os

from dotenv import load_dotenv
from openrouter import OpenRouter


def compute_embedding(content: str) -> list[float]:
    """Generate a numeric embedding for the given content via OpenRouter."""
    if not content.strip():
        raise ValueError("content must not be empty")

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY must be set")

    with OpenRouter(api_key=api_key) as client:
        response = client.embeddings.generate(
            model="openai/text-embedding-3-small",
            input=content,
            encoding_format="float",
        )

    if not response.data:
        raise ValueError("OpenRouter returned no embedding")

    embedding = response.data[0].embedding
    if not isinstance(embedding, list) or not embedding:
        raise ValueError("OpenRouter returned no numeric embedding")

    return embedding
