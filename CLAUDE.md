# Project: Alien

## Overview
A series of scripts to generate images of aliens. All images

## Tech stack
- Python 3.12, managed with uv
- Testing: pytest

## Commands
- Install deps: `uv sync`
- Run tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Run locally: `uv run python main.py`
- Deploy: `terraform apply`

## Project structure
- `src/` — application code
- `tests/` — pytest tests, mirrors src/ structure

## Conventions
- Type hints on all functions
- Config via environment variables, not hardcoded values
- Prefer dicts over dataclasses for structured data passed between functions

## Things to avoid
- Don't commit anything under `.env` or `secrets/`
- Don't add new dependencies without checking if stdlib or an existing dep covers it

## Notes for Claude
- Run `ruff check` after making changes, fix any new warnings
- Commit each time you have completed some changes and tested it to make sure it works. Give a meaningful commit message.
- Always ask questions if you don't understand.
- Point out what you are least confident about.
- Point out anything you think I am missing.
