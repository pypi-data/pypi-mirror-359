# Contributing to TPPT

We welcome contributions to TPPT! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yassun7010/tppt.git
cd tppt
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Development Tools

TPPT uses several development tools:

- **mypy**: Static type checking
- **pyright**: Additional type checking
- **ruff**: Code formatting and linting
- **pytest**: Testing framework

You can run all checks using:

```bash
uv run task ci
```

Or run individual checks:

```bash
# Format code
uv run task format

# Run linter
uv run task lint

# Run type checker
uv run task typecheck

# Run tests
uv run task test
```

## Pull Request Process

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "Add your feature description"
```

3. Ensure all tests pass:
```bash
uv run task ci
```

4. Push your changes and create a pull request:
```bash
git push origin feature/your-feature-name
```

5. Create a Pull Request on GitHub

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Write tests for new features

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting a pull request
- Add integration tests for complex features
- Test edge cases and error conditions

## Documentation

When adding new features, please:

1. Add docstrings to all new functions and classes
2. Update the relevant documentation files
3. Add examples if appropriate
4. Update the changelog

## Questions or Issues?

If you have questions or run into issues:

1. Check the existing issues on GitHub
2. Create a new issue if needed
3. Join our community discussions

Thank you for contributing to TPPT! 