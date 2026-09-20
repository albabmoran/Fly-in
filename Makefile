PYTHON      := python3
POETRY      := poetry
MAIN        := fly-in.py
MAP        	?= maps/easy/01_linear_path.txt

GREEN       := \033[1;32m
BLUE        := \033[1;34m
YELLOW      := \033[1;33m
RESET       := \033[0m

MYPY_FLAGS  := --warn-return-any \
			   --warn-unused-ignores \
			   --ignore-missing-imports \
			   --disallow-untyped-defs \
			   --check-untyped-defs

install:
	@if ! command -v poetry >/dev/null 2>&1; then \
		echo "$(YELLOW) -> Poetry not found. Installing...$(RESET)"; \
		$(PYTHON) -m pip install poetry; \
	fi
	@echo "$(BLUE) -> Installing project dependencies with Poetry $(RESET)"
	@$(POETRY) install --quiet
	@echo "$(GREEN) -> Installation Complete!$(RESET)"

run:
	@echo "$(BLUE) -> Running $(MAIN) with $(MAP) $(RESET)"
	@mkdir -p data
	@PYGAME_HIDE_SUPPORT_PROMPT=1 $(POETRY) run $(PYTHON) $(MAIN) $(MAP)

debug:
	@echo "$(BLUE) -> Starting the debugger (PDB) $(RESET)"
	@PYGAME_HIDE_SUPPORT_PROMPT=1 $(POETRY) run $(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	@echo "$(YELLOW) -> Deleting Temporary Files and Cache $(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "$(GREEN) -> Cleaning complete! $(RESET)"

lint:
	@echo "$(YELLOW) -> Passing the Linter (flake8 and Mypy) $(RESET)"
	@$(POETRY) run flake8 . --exclude=.venv
	@$(POETRY) run mypy . $(MYPY_FLAGS)
	@echo "$(GREEN) -> Clean, well-typed code!$(RESET)"

lint-strict:
	@echo "$(YELLOW) -> Passing the STRICT Linter (flake8 and Mypy) $(RESET)"
	@$(POETRY) run flake8 . --exclude=.venv
	@$(POETRY) run mypy . --strict
	@echo "$(GREEN) -> Perfect! Code is 100%% strict and well-typed!$(RESET)"

.PHONY: install run debug clean lint lint-strict