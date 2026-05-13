# Contributing to Vidoor

Thank you for your interest in contributing to Vidoor.

We welcome high-quality contributions that improve:
- Stability
- Performance
- Cross-platform compatibility
- User experience
- Test coverage
- Documentation

---

# Development Environment

## Requirements

- Python 3.10+
- Node.js
- FFmpeg

---

# Setup

## Clone Repository

```bash
git clone https://github.com/Leli254/Vidoor.git
cd Vidoor
```


Create Virtual Environment

Linux / macOS
```python -m venv venv```
```source venv/bin/activate```

Windows
```
python -m venv venv
venv\Scripts\activate
```
Install Dependencies
```pip install -r requirements.txt```

Running the Application
    ```python main.py```

### Running Tests
All Tests
```pytest -v```

GUI Tests
```pytest tests/gui -v```

### Code Standards

Contributors are expected to:

- Write clear, maintainable code
- Preserve cross-platform compatibility
- Include tests where appropriate
- Follow existing project structure and naming conventions

### Pull Request Guidelines

Before submitting a pull request:

- Ensure all tests pass
- Keep commits focused and atomic
- Include a clear description of changes
- Avoid unrelated formatting-only modifications
- Reporting Issues

### When reporting bugs, include:

- Operating system
- Python version
- FFmpeg version
- Reproduction steps
- Relevant logs or screenshots

### Security

Please do not publicly disclose security vulnerabilities.

Open a private issue or contact the maintainers directly for responsible disclosure.

Thank you for helping improve Vidoor.
