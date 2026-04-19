import os

from agent.memory import (
    append_memory,
    load_memory,
    save_memory,
    trim_messages_to_token_budget,
)
from openai import OpenAI


SYSTEM_PROMPT = "You are tobi, a helpful AI assistant."


def ask_model(
    prompt: str,
    model: str,
    timeout: float | None = None,
    use_memory: bool = True,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key, timeout=timeout)
    memory_history = load_memory() if use_memory else []
    memory_history = trim_messages_to_token_budget(memory_history)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *memory_history,
        {"role": "user", "content": prompt},
    ]

    response = client.responses.create(
        model=model,
        input=messages,
    )

    output_text = response.output_text.strip()

    if use_memory:
        updated_memory = append_memory(memory_history, "user", prompt)
        updated_memory = append_memory(updated_memory, "assistant", output_text)
        save_memory(updated_memory)

    return output_text
