# tobi-cli-ai-agent

A minimal Python CLI built with `typer` and the OpenAI SDK.

It supports direct prompting and a simple multi-step AI agent mode that can plan tasks, suggest shell commands, ask for confirmation, execute them, and retry with a suggested fix when a command fails.

## Features

- `tobi "prompt"`
  Uses `gpt-4o`

- `tobi fast "prompt"`
  Uses `gpt-4o-mini`

- `tobi deep "prompt"`
  Uses `gpt-4.1`

- `tobi run "task"`
  Runs a multi-step AI agent workflow:
  - Breaks a task into steps
  - Converts each step into one bash command
  - Shows the command before execution
  - Always asks for confirmation
  - Executes with `subprocess`
  - Detects errors
  - Suggests a fixed command and asks to retry
  - Blocks dangerous commands like `rm -rf /`, `mkfs`, and `shutdown`

- Short-term memory
  - Stores recent user and assistant messages in `~/.tobi_history.json`
  - Keeps only the latest messages with automatic trimming
  - Trims long context before sending it to the model

- `tobi reset`
  Clears local memory history

## Project Structure

```text
tobi-cli-ai-agent/
├── cli.py
├── pyproject.toml
├── requirements.txt
├── core/
│   └── llm.py
└── agent/
    ├── memory.py
    ├── planner.py
    ├── loop.py
    └── executor.py
```

## Requirements

- Python 3.10+
- An OpenAI API key

## Installation

### macOS / Linux

```bash
cd {your_dir}/tobi-cli-ai-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -e . --no-build-isolation
export OPENAI_API_KEY=your_api_key_here
```

### Linux Notes

If `python3 -m venv` is missing on Linux, install the venv package first.

Ubuntu / Debian:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Fedora:

```bash
sudo dnf install python3 python3-pip
```

Arch Linux:

```bash
sudo pacman -S python python-pip
```

Then install the CLI:

```bash
git clone https://github.com/tobi-hung-nguyen/tobi-cli-ai-agent.git
cd tobi-cli-ai-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -e . --no-build-isolation
export OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Prompt

```bash
tobi "What is Docker?"
```

### Fast Mode

```bash
tobi fast "Summarize Python in one sentence"
```

### Deep Mode

```bash
tobi deep "Explain how containers work"
```

### Agent Mode

```bash
tobi run "setup nginx with docker"
```

### Reset Memory

```bash
tobi reset
```

### Add `tobi` to Shell PATH

If `tobi` is not found in a new shell, add the virtualenv binary path to your shell config.

`zsh`:

```bash
echo 'export PATH="{your_dir}/tobi-cli-ai-agent/.venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

`bash`:

```bash
echo 'export PATH="{your_dir}/tobi-cli-ai-agent/.venv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Example flow:

```text
🧠 Task: setup nginx with docker
Planning...

👉 Step 1: pull nginx image
⚡ docker pull nginx
Execute? (y/n)

👉 Step 2: run container
⚡ docker run -d -p 80:80 nginx
Execute? (y/n)
```

If a command fails, the CLI will show the error, ask the model for a fixed command, then prompt:

```text
Suggested fix: <command>
Retry? (y/n)
```

### Memory Behavior

The CLI keeps short-term memory in:

```bash
~/.tobi_history.json
```

It stores messages in this format:

```json
[
  { "role": "user", "content": "..." },
  { "role": "assistant", "content": "..." }
]
```

Memory rules:

- Only recent messages are kept
- Old messages are automatically removed
- Long responses are truncated before saving
- Context is trimmed before sending to the model

### Test Memory

```bash
tobi "My name is Hung"
tobi "What is my name?"
```

Inspect memory:

```bash
cat ~/.tobi_history.json
```

## Safety

- No command is executed automatically
- Every command requires user confirmation
- Known dangerous commands are blocked
- Memory is automatically trimmed and never grows forever

## Notes

- `tobi run` is interactive by design
- Command quality depends on the model output
- The current implementation is intentionally minimal and modular
- The CLI is installed via the `tobi` command from `pip install -e .`
- `tobi`, `fast`, and `deep` use short-term memory
- `tobi reset` clears saved context

## License

This project is licensed under the MIT License. See the [LICENSE]({your_dir}/tobi-cli-ai-agent/LICENSE) file.
