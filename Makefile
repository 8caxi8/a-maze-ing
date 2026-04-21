MAIN = a_maze_ing.py

install:
	uv sync

run:
	uv run python3 $(MAIN)

debug:
	uv run python3 pdb $(MAIN)

clean:
	find . -name "__pycache__" -print -exec rm -rf {} +
	find . -name ".mypy_cache" -print -exec rm -rf {} +
	find . -name "*.pyc" -print -delete

lint:
	uv run flake8 --exclude=.venv,llm_sdk .
	uv run mypy . --exclude '\.venv|llm_sdk' --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 --exclude=.venv,llm_sdk .
	uv run mypy . --exclude '\.venv|llm_sdk' --strict

.PHONY: install run debug clean lint lint-strict
