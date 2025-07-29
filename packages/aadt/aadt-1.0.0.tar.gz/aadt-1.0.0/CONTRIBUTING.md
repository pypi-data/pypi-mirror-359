# Contributing to Anki Add-on Builder (AADT)

Thank you for your interest in contributing to AADT! This guide will help you get started.

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (modern type annotations required)
- **uv** (recommended) or pip for dependency management
- **Git** (optional but recommended)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/glutanimate/anki-addon-builder.git
cd anki-addon-builder

# Install dependencies with uv (recommended)
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"
```

## 📋 Development Guidelines

### Code Quality Standards

AADT follows modern Python best practices:

- **Type Safety**: Complete type annotations required (`mypy` validation)
- **Code Formatting**: Uses `ruff` for linting and formatting
- **Modern Python**: Takes advantage of Python 3.10+ features (union types, match statements, etc.)

### Running Quality Checks

```bash
# Lint and format code
uv run ruff check aadt/
uv run ruff format aadt/

# Type checking (when available)
uv run mypy aadt/

# Run tests
uv run pytest

# With coverage
uv run pytest --cov=aadt
```

### Code Style

- **Modern Python syntax**: Use `str | None` instead of `Optional[str]`
- **Type annotations**: All functions and methods must have complete type hints
- **Error handling**: Use exception chaining (`raise ... from e`)
- **Dataclasses**: Prefer dataclasses over plain classes where appropriate
- **Pathlib**: Use `pathlib.Path` instead of string paths

### Architecture Principles

1. **Git-optional design**: Features should work both with and without Git
2. **Type safety**: Leverage Python's type system for better code reliability
3. **Configurable**: Allow users to customize behavior through `addon.json`
4. **Error transparency**: Provide clear, actionable error messages
5. **Modern tooling**: Use contemporary Python development tools (uv, ruff, etc.)

## 🧪 Testing

- Write tests for new features and bug fixes
- Ensure tests pass in both Git and non-Git environments
- Test configuration parsing and validation
- Verify error handling with meaningful messages

## 📝 Documentation

When making changes:

- Update relevant docstrings
- Update README.md if adding new features
- Update schema.json for new configuration options
- Consider updating examples in documentation

## 🔧 Debugging

### Useful Commands

```bash
# Test with verbose output
uv run aadt build -v

# Test in non-Git environment
cd /tmp && mkdir test-addon && cd test-addon
aadt init test-addon -y
aadt build -v

# Test configuration parsing
python -c "from aadt.config import Config; print(Config().as_dataclass())"
```

## 🎯 Areas for Contribution

- **Error handling improvements**: Better error messages and recovery
- **Performance optimization**: Faster builds and file operations
- **Documentation**: Examples, tutorials, and API documentation
- **Testing**: Edge cases, platform compatibility, error scenarios
- **Feature requests**: Check issues for community needs

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create a feature branch** from `main`
3. **Make your changes** following the guidelines above
4. **Run quality checks** and ensure they pass
5. **Write tests** for new functionality
6. **Update documentation** as needed
7. **Submit a pull request** with a clear description

### PR Description Template

```markdown
## Changes
- Brief description of what changed

## Testing
- How you tested the changes
- Any edge cases considered

## Documentation
- Documentation updates made (if any)

## Breaking Changes
- Any breaking changes and migration notes
```

## 🤝 Community

- Be respectful and constructive in discussions
- Help others by reviewing PRs and answering questions
- Report bugs with detailed reproduction steps
- Suggest improvements through issues

Thanks for contributing to AADT! 🎉