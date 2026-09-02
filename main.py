import os
from dotenv import load_dotenv
from llm import LLM
from models import BoolResponse

MODEL_NAME = "gpt-5.6-luna"
REASONING_EFFORT = "low"

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    llm = LLM(
        api_key=api_key,
        model=MODEL_NAME,
        reasoning_effort=REASONING_EFFORT,
        instructions="You are a helpful assistant",
    )

    print(llm.E("Is 2 + 2 = 5?", BoolResponse))
