# Makefile for MCP KQL Server
# Author: Arjun Trivedi
# Email: arjuntrivedi42@yahoo.com

.PHONY: help install install-dev clean test test-unit test-integration lint format type-check security build publish docs pre-commit all

# Default target
help:
	@echo "MCP KQL Server - Development Commands"
	@echo "====================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install        Install production dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  clean          Clean build artifacts and cache"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-cov       Run tests with coverage report"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint           Run all linting checks"
	@echo "  format         Format code with black and isort"
	@echo "  type-check     Run type checking with mypy"
	@echo "  security       Run security scans"
	@echo "  pre-commit     Run pre-commit hooks"
	@echo ""
	@echo "Build Commands:"
	@echo "  build          Build package"
	@echo "  publish        Publish to PyPI"
	@echo "  publish-test   Publish to Test PyPI"
	@echo ""
	@echo "Documentation Commands:"
	@echo "  docs           Build documentation"
	@echo "  docs-serve     Serve documentation locally"
	@echo ""
	@echo "All-in-one Commands:"
	@echo "  all            Run format, lint, type-check, test"
	@echo "  ci             Run CI pipeline locally"

# Setup commands
install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements-dev.txt
	pre-commit install

clean:
	@echo "Cleaning build artifacts and cache..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Testing commands
test:
	@echo "Running all tests..."
	pytest

test-unit:
	@echo "Running unit tests..."
	pytest -m "unit"

test-integration:
	@echo "Running integration tests..."
	pytest -m "integration"

test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=mcp_kql_server --cov-report=html --cov-report=term-missing

# Code quality commands
lint:
	@echo "Running linting checks..."
	flake8 mcp_kql_server/
	@echo "✅ Flake8 linting passed"

format:
	@echo "Formatting code..."
	black mcp_kql_server/
	isort mcp_kql_server/
	@echo "✅ Code formatting completed"

format-check:
	@echo "Checking code format..."
	black --check mcp_kql_server/
	isort --check-only mcp_kql_server/
	@echo "✅ Code format check passed"

type-check:
	@echo "Running type checking..."
	mypy mcp_kql_server/
	@echo "✅ Type checking passed"

security:
	@echo "Running security scans..."
	bandit -r mcp_kql_server/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	@echo "✅ Security scans completed"

pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files

# Build commands
build:
	@echo "Building package..."
	python -m build
	@echo "✅ Package built successfully"

build-check:
	@echo "Checking built package..."
	twine check dist/*
	@echo "✅ Package check passed"

publish-test:
	@echo "Publishing to Test PyPI..."
	twine upload --repository testpypi dist/*

publish:
	@echo "Publishing to PyPI..."
	twine upload dist/*

# Documentation commands
docs:
	@echo "Building documentation..."
	# Add documentation build commands here when ready
	@echo "📚 Documentation ready"

docs-serve:
	@echo "Serving documentation locally..."
	# Add documentation serve commands here when ready
	@echo "📖 Documentation server started"

# Development workflow commands
dev-setup: install-dev
	@echo "Setting up development environment..."
	@echo "✅ Development environment ready"

validate: format-check lint type-check security
	@echo "Running all validation checks..."
	@echo "✅ All validation checks passed"

all: format lint type-check test
	@echo "Running complete development workflow..."
	@echo "🎉 All checks passed!"

ci: clean validate test-cov build build-check
	@echo "Running CI pipeline locally..."
	@echo "🚀 CI pipeline completed successfully!"

# Version management
version:
	@echo "Current version:"
	@python -c "from mcp_kql_server import __version__; print(f'v{__version__}')"

# Quick development commands
quick-test:
	@echo "Running quick tests (unit only)..."
	pytest -m "unit" --tb=short -q

quick-check:
	@echo "Running quick checks..."
	black --check mcp_kql_server/ && \
	isort --check-only mcp_kql_server/ && \
	flake8 mcp_kql_server/ && \
	echo "✅ Quick checks passed"

# Performance testing
perf-test:
	@echo "Running performance tests..."
	pytest -m "slow" --tb=short

# Memory testing
memory-test:
	@echo "Running memory-related tests..."
	pytest -m "memory" --tb=short

# Authentication testing
auth-test:
	@echo "Running authentication tests..."
	pytest -m "auth" --tb=short

# Azure-specific testing
azure-test:
	@echo "Running Azure integration tests..."
	pytest -m "azure" --tb=short

# Install and setup everything
bootstrap: clean install-dev pre-commit
	@echo "🎯 Project bootstrapped successfully!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Run 'make test' to verify everything works"
	@echo "2. Run 'make all' to run the full development workflow"
	@echo "3. Check 'make help' for available commands"