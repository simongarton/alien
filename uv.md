## Using UV

### Quick notes

Use the `venv` approach:

`source .venv/bin/activate`

Trying the other way worked, but then I found a `src/alien/__init__.py` file which "wasn't used" but
if I deleted it, it vanished.

### Claude conversation

how do I go about starting a project using uv ?

Here's the basic flow:

1. Install uv (if not already)

bash
curl -LsSf https://astral.sh/uv/install.sh | sh. # did this one
(or brew install uv on macOS)

2. Start a new project

bash
uv init myproject
cd myproject
This creates pyproject.toml, a .python-version file, a README.md, and a main.py/src/ layout. If you're starting inside an existing directory instead:

bash
uv init
3. Pin a Python version (optional but useful)

bash
uv python pin 3.12
uv will download and manage that Python version itself if you don't have it — no separate pyenv needed.

4. Add dependencies

bash
uv add requests boto3
uv add --dev pytest ruff
This updates pyproject.toml, resolves and writes uv.lock, and creates/updates a .venv automatically — you never have to manually activate anything for uv run to work.

5. Run things

bash
uv run python main.py
uv run pytest
uv run transparently uses the project's locked environment.

6. Sync an existing project (e.g. after cloning one, or in CI)

bash
uv sync
Reads uv.lock and builds/updates .venv to match exactly.

A few things worth knowing given your AWS/CDK workflow:

uv.lock is a real cross-platform lockfile with hashes — commit it.
If you need an activated shell instead of prefixing every command with uv run, .venv is a completely normal venv: source .venv/bin/activate works as usual.
For scripts outside a project (e.g. a one-off Lambda test script), uv run --with boto3 script.py will run it in an ephemeral environment without any project setup at all — handy for quick throwaway tooling.
Migrating an existing requirements.txt project: uv add -r requirements.txt will pull them into pyproject.toml and lock them.
That's really the whole workflow — uv add/uv run/uv sync covers 95% of day-to-day use.
