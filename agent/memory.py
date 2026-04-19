import json
from pathlib import Path


MEMORY_PATH = Path.home() / ".tobi_history.json"
MAX_MESSAGES = 20
MAX_MESSAGE_CHARS = 4000
MAX_CONTEXT_TOKENS = 4000


def load_memory() -> list[dict[str, str]]:
    if not MEMORY_PATH.exists():
        return []

    try:
        data = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    messages: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if isinstance(role, str) and isinstance(content, str):
            messages.append({"role": role, "content": truncate_content(content)})

    return trim_messages(messages)


def save_memory(messages: list[dict[str, str]]) -> None:
    trimmed = trim_messages(messages)
    MEMORY_PATH.write_text(
        json.dumps(trimmed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clear_memory() -> None:
    if MEMORY_PATH.exists():
        MEMORY_PATH.unlink()


def append_memory(messages: list[dict[str, str]], role: str, content: str) -> list[dict[str, str]]:
    updated = list(messages)
    updated.append({"role": role, "content": truncate_content(content)})
    return trim_messages(updated)


def trim_messages(messages: list[dict[str, str]], max_messages: int = MAX_MESSAGES) -> list[dict[str, str]]:
    cleaned = [
        {"role": message["role"], "content": truncate_content(message["content"])}
        for message in messages
        if message.get("role") and message.get("content")
    ]
    return cleaned[-max_messages:]


def trim_messages_to_token_budget(
    messages: list[dict[str, str]],
    max_tokens: int = MAX_CONTEXT_TOKENS,
) -> list[dict[str, str]]:
    trimmed = trim_messages(messages)

    while trimmed and estimate_messages_tokens(trimmed) > max_tokens:
        trimmed.pop(0)

    return trimmed


def estimate_messages_tokens(messages: list[dict[str, str]]) -> int:
    return sum(estimate_tokens(message["content"]) for message in messages)


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def truncate_content(content: str, max_chars: int = MAX_MESSAGE_CHARS) -> str:
    if len(content) <= max_chars:
        return content
    return content[: max_chars - 3].rstrip() + "..."
