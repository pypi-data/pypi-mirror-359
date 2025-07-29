# Kairix DevTools

[![Tests](https://github.com/kairix-dev/devtools-python/workflows/Tests/badge.svg)](https://github.com/kairix-dev/devtools-python/actions)
[![Coverage](https://codecov.io/gh/kairix-dev/devtools-python/branch/main/graph/badge.svg)](https://codecov.io/gh/kairix-dev/devtools-python)
[![Python](https://img.shields.io/pypi/pyversions/kairix-devtools.svg)](https://pypi.org/project/kairix-devtools/)
[![PyPI version](https://badge.fury.io/py/kairix-devtools.svg)](https://badge.fury.io/py/kairix-devtools)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

> 🚀 **Professional Python development tools** for async/await analysis, code quality, and CI/CD integration.

A comprehensive CLI library for development tools that can be used with pre-commit hooks, manually, or in CI/CD pipelines.

## 🚀 Quick Start

```bash
# Install
pip install kairix-devtools

# Check async/await usage in your code
kairix-devtools asyncio check-await src/

# Get JSON output for tooling integration
kairix-devtools asyncio check-await src/ --output-format json
```

## 📋 Features

### 🔄 Asyncio Analysis Tools

Advanced async/await validation that helps you catch common async programming mistakes:

- ✅ **Missing await detection** - Finds async functions called without `await`
- ✅ **Missing asyncio context** - Detects async functions called outside async context
- ✅ **Smart asyncio.gather handling** - Correctly handles coroutines passed to `gather()`
- ✅ **Type-aware analysis** - Respects functions typed to return coroutines
- ✅ **Comprehensive reporting** - Human-friendly and JSON output formats

## 📖 Documentation

- [📚 Full Documentation](docs/README.md)
- [🔄 Asyncio Commands](docs/asyncio.md)
- [⚙️ CLI Overview](docs/cli.md)

## 💡 Common Use Cases

### 1. Pre-commit Hook

Catch async/await issues before they reach your repository:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-async-await
        name: Check async/await usage
        entry: kairix-devtools asyncio check-await
        language: system
        files: \.py$
        args: ["--output-format", "human"]
```

### 2. CI/CD Integration

GitHub Actions example:

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  async-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12.x'
      - name: Install kairix-devtools
        run: pip install kairix-devtools
      - name: Check async/await usage
        run: kairix-devtools asyncio check-await src/ --output-format json
```

### 3. Local Development

Quick checks during development:

```bash
# Check specific file
kairix-devtools asyncio check-await my_async_module.py

# Check directory with exclusions
kairix-devtools asyncio check-await src/ --exclude "test_*" --exclude "*_legacy.py"

# JSON output for further processing
kairix-devtools asyncio check-await src/ --output-format json | jq '.violations | length'
```

## 🎯 Practical Examples

### ❌ Issues Detected

```python
# Missing await in async function
async def fetch_user_data():
    user = get_user_async()  # ❌ Missing await
    return user

# Missing asyncio context in sync function  
def main():
    result = fetch_user_data()  # ❌ Missing asyncio.run()
    return result

# Unhandled coroutine
async def process_data():
    fetch_data_async()  # ❌ Created but never awaited
    return "done"
```

### ✅ Correct Patterns Recognized

```python
# Proper asyncio.gather usage
async def fetch_multiple():
    results = await asyncio.gather(
        fetch_data_async("A"),  # ✅ Handled by gather
        fetch_data_async("B")   # ✅ Handled by gather
    )
    return results

# Functions typed to return coroutines
def create_tasks() -> list[Coroutine[Any, Any, str]]:
    return [
        fetch_data_async("A"),  # ✅ Valid: function returns coroutines
        fetch_data_async("B")   # ✅ Valid: function returns coroutines
    ]

# Proper asyncio context
def main():
    result = asyncio.run(fetch_user_data())  # ✅ Correct
    return result
```

## 🔧 Programmatic API

Use kairix-devtools in your own Python tools:

```python
from kairix_devtools.asyncio import AsyncChecker

# Create checker instance
checker = AsyncChecker()

# Check a single file
result = checker.check_file("my_async_code.py")

# Check a directory with exclusions
result = checker.check_directory(
    "src/", 
    exclude_patterns=["test_*", "*_test.py"]
)

# Access results
print(f"Files checked: {result.total_files}")
print(f"Issues found: {result.violation_count}")
print(f"All checks passed: {result.passed}")

# Process violations
for violation in result.violations:
    print(f"Issue in {violation.file_path}:{violation.line_number}")
    print(f"  Function: {violation.function_name}")
    print(f"  Type: {violation.violation_type}")
    print(f"  Code: {violation.source_line}")

# Convert to JSON for external tools
result_json = result.model_dump()
```

## 📊 Output Formats

### Human-Readable Output

```
❌ Async/await violations found!

AsyncViolationError: Function 'fetch_data' called without proper async handling
  Type: missing_await
  💡 Fix: Add 'await' before the function call

🔄 File "example.py", line 15
    result = fetch_data("https://api.example.com")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

📁 Files checked: 3
Violations found: 🔄 missing_await: 1
❌ Check failed!
```

### JSON Output

```json
{
  "total_files": 3,
  "violations": [
    {
      "file_path": "example.py",
      "line_number": 15,
      "column_number": 13,
      "function_name": "fetch_data",
      "violation_type": "missing_await",
      "source_line": "    result = fetch_data(\"https://api.example.com\")"
    }
  ],
  "passed": false,
  "violation_count": 1
}
```

## 🛠️ Installation & Development

### Installation

```bash
# Install from PyPI (when published)
pip install kairix-devtools

# Install from source
git clone https://github.com/your-org/kairix-devtools.git
cd kairix-devtools
pip install -e .
```

### Development Setup

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Run type checking
pyright kairix_devtools/

# Test the tool on itself
kairix-devtools asyncio check-await kairix_devtools/
```

## 🤝 Contributing

We love contributions! There are many ways you can help:

### 🚀 Ways to Contribute

- 🐛 **Report Bugs** - Use our [issue templates](.github/ISSUE_TEMPLATE/)
- ✨ **Propose Features** - Share your ideas to improve the tool
- 📚 **Improve Documentation** - Help other users with better docs
- 🧪 **Write Tests** - Improve code coverage and quality
- 🔧 **Development** - Implement new features or fix bugs

### 📋 Quick Start for Contributors

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/devtools-python.git
cd devtools-python

# 2. Set up the development environment
# This project uses a devcontainer for a consistent development environment.
# Simply open the project in VS Code with the Dev Containers extension installed.

# If you prefer a manual setup:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"

# 3. Install pre-commit hooks
pre-commit install

# 4. Run tests to verify everything works
pytest
```

### 📖 Contributor Resources

- 📚 **[Contribution Guide](CONTRIBUTING.md)** - Complete step-by-step guide
- 🛠️ **[Development Guide](docs/DEVELOPMENT.md)** - Local setup and development workflow
- 🐛 **[Report a Bug](.github/ISSUE_TEMPLATE/bug_report.yml)** - Template for reporting issues
- ✨ **[Propose a Feature](.github/ISSUE_TEMPLATE/feature_request.yml)** - Template for new ideas
- ❓ **[Ask a Question](.github/ISSUE_TEMPLATE/question.yml)** - Template to get help

### 🏆 Acknowledgments

We thank all our contributors who make this project possible. Their contributions are featured in:

- GitHub's list of contributors
- Release notes for significant changes
- Special mentions for major contributions

## 📄 License

This project is licensed under the Unlicense - see the [LICENSE](LICENSE) file for details.