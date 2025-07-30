# Python Package Development & Testing Overview

This guide outlines the structure and tools commonly used in Python package development, with a focus on managing dependencies, testing, and configuration.

---

## 📦 Dependency Management

### `requirements.txt`
- Lists **production dependencies** required to run the Python application.
- Installed in production environments to keep builds minimal and fast.

### `requirements_dev.txt`
- Lists **development and testing dependencies**.
- Used by developers to set up a full-featured environment including tools for testing, linting, etc.

---

## ⚙️ Project Configuration

### `setup.cfg`
- Used by `setuptools` to define **package metadata** and **installation behavior**.
- Contains:
  - Package name, version, author, license
  - Dependencies
  - Entry points
  - Metadata for PyPI

### `pyproject.toml`
- A modern configuration file introduced by [PEP 518](https://peps.python.org/pep-0518/).
- Defines the **build system** and can replace `setup.cfg`.
- Compatible with tools like Poetry, Flit, and modern `setuptools`.

---

## 🧪 Testing

### 🔍 Testing Types
- **Manual Testing**: Done by a human to check functionality.
- **Automated Testing**: Code-based testing, executed automatically.

### 🧱 Modes of Testing
- **Unit Testing**: Tests individual components or functions in isolation.
- **Integration Testing**: Ensures different modules or services work together.

### 🧪 Testing Frameworks
| Framework       | Purpose                              |
|----------------|--------------------------------------|
| `pytest`        | Simple and powerful testing tool     |
| `unittest`      | Built-in Python testing framework    |
| `robotframework`| For acceptance testing               |
| `selenium`      | UI/browser testing                   |
| `behave`        | BDD (Behavior Driven Development)    |
| `doctest`       | Test code embedded in docstrings     |

---

## 📁 Linting & Code Quality

### Tools for Style Checking
- **`pylint`** – Comprehensive linting
- **`flake8`** – Combines:
  - `pycodestyle` (PEP8 checks)
  - `pyflakes` (error detection)
  - `mccabe` (complexity checking)

---

## 🔄 Testing Automation with `tox`

### What is `tox`?
- Automates testing across **multiple Python versions**.
- Creates isolated virtual environments.
- Installs dependencies and runs defined commands.

### How `tox` Works:
1. Creates isolated environments with `virtualenv`
2. Installs dev and test dependencies
3. Runs test and lint commands
4. Outputs results for each environment

### `tox` vs others:
- It's like a combination of **virtualenvwrapper** + **Makefile** functionality.

---

## 🧪 Example `tox.ini`

```ini
[tox]
envlist = py38, py39, lint

[testenv]
deps = 
    pytest
commands = 
    pytest tests/

[testenv:lint]
deps = 
    flake8
commands = 
    flake8 package_name/
