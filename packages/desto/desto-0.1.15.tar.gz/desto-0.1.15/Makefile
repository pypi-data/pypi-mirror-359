# Makefile for desto package management

.PHONY: help bump-patch bump-minor bump-major release-patch release-minor release-major build test lint clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Version bumping
bump-patch:  ## Bump patch version (0.1.14 -> 0.1.15)
	python scripts/bump_version.py patch

bump-minor:  ## Bump minor version (0.1.14 -> 0.2.0)
	python scripts/bump_version.py minor

bump-major:  ## Bump major version (0.1.14 -> 1.0.0)
	python scripts/bump_version.py major

# Release process
release-patch:  ## Bump patch version and create release
	./scripts/release.sh patch

release-minor:  ## Bump minor version and create release
	./scripts/release.sh minor

release-major:  ## Bump major version and create release
	./scripts/release.sh major

# Development
test:  ## Run tests
	uv run pytest tests/

lint:  ## Run linting
	uv run ruff check .

build:  ## Build package
	uv build

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/

# Quick development tasks
dev-install:  ## Install package in development mode
	uv pip install -e .

publish:  ## Publish to PyPI (after manual review)
	uv publish

# Show current version
version:  ## Show current version
	@python -c "from src.desto._version import __version__; print(f'Current version: {__version__}')"
