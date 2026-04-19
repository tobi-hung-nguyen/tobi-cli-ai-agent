import re
import subprocess

from core.llm import ask_model


COMMAND_MODEL = "gpt-4o-mini"
COMMAND_TIMEOUT_SECONDS = 20.0
DANGEROUS_PATTERNS = (
    "rm -rf /",
    "mkfs",
    "shutdown",
)


def generate_command(task: str) -> str:
    prompt = (
        "Convert the user's request into exactly one short bash command. "
        "Return only the command as a single line. No markdown. No explanation. "
        "Prefer safe, read-only commands when possible.\n\n"
        f"Task: {task}"
    )
    response = ask_model(
        prompt=prompt,
        model=COMMAND_MODEL,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )
    return normalize_command(response)


def generate_command_for_step(step: str) -> str:
    prompt = (
        "Convert this execution step into exactly one bash command. "
        "Return only the command as a single line. No markdown. No explanation.\n\n"
        f"Step: {step}"
    )
    response = ask_model(
        prompt=prompt,
        model=COMMAND_MODEL,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )
    return normalize_command(response)


def generate_fix_command(step: str, failed_command: str, error_output: str) -> str:
    prompt = (
        "A bash command failed. Return one corrected bash command only. "
        "Return only the command as a single line. No markdown. No explanation.\n\n"
        f"Step: {step}\n"
        f"Failed command: {failed_command}\n"
        f"Error output: {error_output}"
    )
    response = ask_model(
        prompt=prompt,
        model=COMMAND_MODEL,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )
    return normalize_command(response)


def normalize_command(command: str) -> str:
    cleaned = command.strip()
    cleaned = cleaned.removeprefix("```bash").removeprefix("```sh").removeprefix("```")
    cleaned = cleaned.removesuffix("```").strip()
    return re.sub(r"\s+", " ", cleaned)


def is_dangerous_command(command: str) -> bool:
    lowered = command.lower()
    return any(pattern in lowered for pattern in DANGEROUS_PATTERNS)


def execute_command(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        executable="/bin/bash",
        text=True,
        capture_output=True,
    )
