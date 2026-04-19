from core.llm import ask_model


PLANNER_MODEL = "gpt-4o"
PLANNER_TIMEOUT_SECONDS = 30.0


def plan_task(task: str) -> list[str]:
    prompt = (
        "Break the user's task into a short ordered list of actionable shell steps. "
        "Return only the steps, one per line. No markdown. No explanations. "
        "Keep the list concise and practical.\n\n"
        f"Task: {task}"
    )
    response = ask_model(
        prompt=prompt,
        model=PLANNER_MODEL,
        timeout=PLANNER_TIMEOUT_SECONDS,
    )
    return parse_steps(response)


def parse_steps(raw_steps: str) -> list[str]:
    steps: list[str] = []
    for line in raw_steps.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        cleaned = cleaned.lstrip("-* ").strip()
        if ". " in cleaned and cleaned.split(". ", 1)[0].isdigit():
            cleaned = cleaned.split(". ", 1)[1].strip()
        if cleaned:
            steps.append(cleaned)
    return steps
