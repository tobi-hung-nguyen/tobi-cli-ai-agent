import typer

from agent.executor import (
    execute_command,
    generate_command_for_step,
    generate_fix_command,
    is_dangerous_command,
)
from agent.planner import plan_task


def run_task(task: str) -> None:
    typer.echo(f"🧠 Task: {task}")
    typer.echo("Planning...")

    steps = plan_task(task)
    if not steps:
        typer.echo("Error: failed to create a plan.", err=True)
        return

    for index, step in enumerate(steps, start=1):
        typer.echo("")
        typer.echo(f"👉 Step {index}: {step}")

        command = generate_command_for_step(step)
        if not command:
            typer.echo("Error: failed to generate a command.", err=True)
            continue

        typer.echo(f"⚡ {command}")

        if is_dangerous_command(command):
            typer.echo("Warning: dangerous command detected. Execution skipped.", err=True)
            continue

        if not typer.confirm("Execute?", default=False):
            continue

        result = execute_command(command)
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                typer.echo(output)
            continue

        error_output = result.stderr.strip() or result.stdout.strip() or "Command failed."
        typer.echo(f"Error: {error_output}", err=True)

        fixed_command = generate_fix_command(
            step=step,
            failed_command=command,
            error_output=error_output,
        )
        if not fixed_command:
            continue

        typer.echo(f"Suggested fix: {fixed_command}")

        if is_dangerous_command(fixed_command):
            typer.echo("Warning: dangerous command detected. Retry skipped.", err=True)
            continue

        if not typer.confirm("Retry?", default=False):
            continue

        retry_result = execute_command(fixed_command)
        if retry_result.returncode != 0:
            retry_error = retry_result.stderr.strip() or retry_result.stdout.strip() or "Command failed."
            typer.echo(f"Error: {retry_error}", err=True)
            continue

        retry_output = retry_result.stdout.strip()
        if retry_output:
            typer.echo(retry_output)
