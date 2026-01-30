.PHONY: install install-dev install-deps uninstall clean format lint test test-verbose test-coverage coverage default

# Detect Python command (works on Windows and Unix)
PYTHON := python

# Default target: run all checks
default: format lint test coverage

# Installation targets
install:
	$(PYTHON) -m pip install .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

install-deps:
	$(PYTHON) -m pip install -e ".[dev]"

uninstall:
	$(PYTHON) -m pip uninstall -y ap-move-lights-to-data

# Development targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf ap_move_lights_to_data.egg-info
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Format code with black
format: install-dev
	$(PYTHON) -m black ap_move_lights_to_data tests

# Lint code with flake8 (disable multiprocessing to avoid sandbox issues, match black line length)
lint: install-dev
	$(PYTHON) -m flake8 --jobs=1 --max-line-length=88 --extend-ignore=E203,E266,E501,W503,F401,W605,E722 ap_move_lights_to_data tests

# Testing (install deps first, then run tests)
test: install-dev
	$(PYTHON) -m pytest

test-verbose: install-dev
	$(PYTHON) -m pytest -v

test-coverage: install-dev
	$(PYTHON) -m pytest --cov=ap_move_lights_to_data --cov-report=html --cov-report=term

# Coverage report (terminal output only)
coverage: install-dev
	$(PYTHON) -m pytest --cov=ap_move_lights_to_data --cov-report=term
