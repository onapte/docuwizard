import subprocess
import os

from openai import OpenAI
from .prompt_type import Prompt
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def query_local_llm(prompt, model="mistral"):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode('utf-8'),
            capture_output=True,
            check=True
        )

        return result.stdout.decode('utf-8')
    
    except subprocess.CalledProcessError as e:
        return f"Local LLM error: {e.stderr.decode('utf-8')}"
    


def query_via_openrouter(prompt: Prompt):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY,
    )

    content = f"""
    Context:
    {prompt.context}

    Question:
    {prompt.question}

    Answer:
    """

    completion = client.chat.completions.create(
    extra_headers={},
    extra_body={},
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[
        {
            "role": "system",
            "content": "You are a question-answering assistant"
        },
        {
            "role": "user",
            "content": content
        }
    ]
    )

    return completion.choices[0].message.content