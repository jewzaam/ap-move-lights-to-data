.PHONY: install install-dev uninstall clean format lint test test-verbose test-coverage coverage

install:
	pip install .

install-dev:
	pip install -e ".[dev]"

uninstall:
	pip uninstall -y ap-move-lights-to-data

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

format:
	black ap_move_lights_to_data tests

lint:
	flake8 ap_move_lights_to_data tests

test:
	pytest

test-verbose:
	pytest -v

test-coverage:
	pytest --cov=ap_move_lights_to_data --cov-report=term-missing

coverage:
	pytest --cov=ap_move_lights_to_data --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"
