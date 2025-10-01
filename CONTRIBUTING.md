# Contributing to LuminaAI

First off, thank you for considering contributing to LuminaAI! It's people like you that make LuminaAI a great platform for multi-agent AI orchestration.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, commands, etc.)
- **Describe the behavior you observed** and explain why it's a problem
- **Explain the behavior you expected to see instead**
- **Include logs, screenshots, or error messages**
- **Specify your environment** (OS, Python version, Kubernetes version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List some examples** of how it would be used
- **Specify if you're willing to work on it**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Ensure all tests pass** (`pytest tests/`)
5. **Lint your code** (`pylint agents/`, `black agents/`, `isort agents/`)
6. **Update documentation** if needed
7. **Write a clear commit message** following our commit guidelines
8. **Submit the pull request** with a description of your changes

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- kubectl (for Kubernetes testing)
- git

### Local Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/LuminaAI.git
cd LuminaAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r agents/planner/requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=agents --cov-report=html

# Run specific test file
pytest tests/test_planner.py -v

# Run with debugging
pytest tests/ -v -s
```

### Code Style

We use the following tools to maintain code quality:

- **black**: Code formatting
- **isort**: Import sorting
- **pylint**: Code linting
- **mypy**: Type checking

```bash
# Format code
black agents/
isort agents/

# Check types
mypy agents/

# Lint code
pylint agents/
```

These checks run automatically via pre-commit hooks.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **88 characters** (black default)
- Use **type hints** for function signatures
- Write **docstrings** for all public functions and classes

Example:

```python
def sanitize_pddl(pddl_string: str) -> str:
    """
    Sanitizes the PDDL string from the LLM to prevent injection attacks.
    
    Args:
        pddl_string: The raw PDDL string to sanitize
        
    Returns:
        The sanitized PDDL string
        
    Raises:
        ValueError: If the PDDL format is invalid
    """
    if not pddl_string.strip().startswith('('):
        raise ValueError("Invalid PDDL plan format")
    return pddl_string
```

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(planner): add support for multiple LLM providers

Implement adapter pattern to support OpenAI, Anthropic, and local models.
This makes the system more flexible and reduces vendor lock-in.

Closes #123
```

```
fix(grpc): handle connection timeout gracefully

Add retry logic and circuit breaker for gRPC connections to prevent
cascading failures.
```

### Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names: `test_<what>_<condition>_<expected_result>`
- Use fixtures for common test setup
- Mock external dependencies (OpenAI API, etc.)

Example:

```python
import pytest
from unittest.mock import Mock, patch

def test_plan_generation_with_valid_prompt_returns_dag():
    """Test that a valid prompt generates a DAG successfully."""
    planner = Planner()
    request = Mock(prompt="Create a plan")
    context = Mock()
    
    response = planner.Plan(request, context)
    
    assert response.dag is not None
    assert "nodes" in response.dag
    assert "edges" in response.dag
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include code examples in docstrings
- Update architecture diagrams if needed
- Keep CHANGELOG.md up to date

## Project Structure Guidelines

When adding new features, follow the existing structure:

```
agents/
  agent_name/
    ├── __init__.py
    ├── main.py           # Entry point
    ├── service.py        # Business logic
    ├── models.py         # Data models
    ├── utils.py          # Utility functions
    ├── Dockerfile
    ├── requirements.txt
    └── agent.proto       # If using gRPC
```

## Review Process

1. **Automated checks** must pass (CI/CD, linting, tests)
2. **At least one maintainer** must review and approve
3. **All conversations** must be resolved
4. **Commits** may be squashed before merging

### What Reviewers Look For

- Code quality and readability
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations
- Backward compatibility

## Getting Help

- **Documentation**: Check the README and docs/
- **Issues**: Search existing issues on GitHub
- **Discussions**: Start a discussion on GitHub Discussions
- **Chat**: Join our community Slack (link in README)
- **Email**: Reach out to dev@bmad.ai

## Recognition

Contributors will be:
- Listed in our CONTRIBUTORS.md file
- Mentioned in release notes
- Eligible for contributor swag (for significant contributions)

Thank you for contributing to LuminaAI! 🚀
