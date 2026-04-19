#!/usr/bin/env python3

import click
import typer
from typer.core import TyperGroup

from agent.memory import clear_memory
from agent.loop import run_task
from core.llm import ask_model


class DefaultPromptGroup(TyperGroup):
    def resolve_command(self, ctx: click.Context, args: list[str]) -> tuple[str, click.Command, list[str]]:
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError:
            command = self.get_command(ctx, "__default__")
            if command is None:
                raise
            return "__default__", command, args


app = typer.Typer(
    add_completion=False,
    help="tobi-cli: a minimal CLI for asking OpenAI models questions.",
    cls=DefaultPromptGroup,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)


def run_prompt(prompt: str, model: str) -> None:
    try:
        response = ask_model(prompt=prompt, model=model, use_memory=True)
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(response)


@app.callback()
def main() -> None:
    return


@app.command("__default__", hidden=True)
def default_prompt(
    prompt_parts: list[str] = typer.Argument(..., help='Prompt to send, for example: tobi "Hello"'),
) -> None:
    run_prompt(prompt=" ".join(prompt_parts), model="gpt-4o")


@app.command()
def fast(prompt: str = typer.Argument(..., help='Prompt to send, for example: tobi fast "Hello"')) -> None:
    run_prompt(prompt=prompt, model="gpt-4o-mini")


@app.command()
def deep(prompt: str = typer.Argument(..., help='Prompt to send, for example: tobi deep "Hello"')) -> None:
    run_prompt(prompt=prompt, model="gpt-4.1")


@app.command()
def run(task: str = typer.Argument(..., help='Task to convert into a bash command, for example: tobi run "list all docker containers"')) -> None:
    try:
        run_task(task)
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def reset() -> None:
    clear_memory()
    typer.echo("Memory cleared")


def entrypoint() -> None:
    app()


if __name__ == "__main__":
    entrypoint()
