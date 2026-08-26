PYTHON      := python3
VENV        := venv
BIN         := $(VENV)/bin
MAIN        := fly-in.py
FILE        ?= maps/easy/01_linear_path.txt
REQ_FILE    := requirements.txt

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
	@echo "$(BLUE) -> Creating virtual environment $(RESET)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(BLUE) -> Installing dependencies from $(REQ_FILE) $(RESET)"
	@$(BIN)/pip install -q -r $(REQ_FILE)
	@echo "$(GREEN) -> Installation Complete!$(RESET)"

run:
	@echo "$(GREEN) -> Running $(MAIN) with $(FILE) $(RESET)"
	@PYGAME_HIDE_SUPPORT_PROMPT=1 $(BIN)/python $(MAIN) $(FILE)

debug:
	@echo "$(YELLOW) -> Starting the debugger (PDB) $(RESET)"
	@PYGAME_HIDE_SUPPORT_PROMPT=1 $(BIN)/python -m pdb $(MAIN) $(FILE)

clean:
	@echo "$(YELLOW) -> Deleting Temporary Files and Cache $(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "$(GREEN) -> Cleaning complete! $(RESET)"

lint:
	@echo "$(YELLOW) -> Passing the Linter (flake8 and Mypy) $(RESET)"
	@$(BIN)/flake8 . --exclude=venv
	@$(BIN)/mypy . $(MYPY_FLAGS)
	@echo "$(GREEN) -> Clean, well-typed code! $(RESET)"

lint-strict:
	@echo "$(YELLOW) -> Passing the STRICT Linter (flake8 and Mypy) $(RESET)"
	@$(BIN)/flake8 . --exclude=venv
	@$(BIN)/mypy . --strict
	@echo "$(GREEN) -> Perfect! Code is 100% strict and well-typed! $(RESET)"

.PHONY: install run debug clean lint lint-strict