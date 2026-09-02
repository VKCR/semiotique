import os
from dotenv import load_dotenv
from openai_tools import create_client, parse_response
from models import TextResponse, BoolResponse

MODEL_NAME = "gpt-5.6-luna"
REASONING_EFFORT = "low"

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = create_client(api_key)

    response = parse_response(
        client,
        model=MODEL_NAME,
        instructions="You are a helpful assistant",
        input="Is 2+2 = 5?",
        reasoning={"effort": REASONING_EFFORT},
        text_format=BoolResponse,
    )

    print(response.output_parsed.response)
