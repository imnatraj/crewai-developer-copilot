# Installation Guide — CrewAI Developer Copilot

This guide describes how to set up the CrewAI Developer Copilot from scratch.

## Prerequisites

Ensure you have the following installed on your system:
* **Python 3.10+** (Python 3.12 is recommended)
* **Node.js 18+** and `npm`
* **sqlite3** (pre-installed with Python)

---

## Installation Steps

### 1. Extract or Clone Project
Move into the project root directory:
```bash
cd crewai-developer-copilot
```

### 2. Configure Python Environment
It is highly recommended to use `uv` (installed on this machine) or `virtualenv` to manage python dependencies.

Using `uv`:
```bash
# Pin python version to 3.12
uv python pin 3.12

# Create and synchronize the virtual environment
uv venv
source .venv/bin/activate
uv sync
```

Alternatively, using standard `venv` and `pip`:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Node.js Tools
The scanner uses `madge` and `dependency-cruiser` to map codebase import networks. Install them locally in the project:
```bash
npm install
```

### 4. Setup environment variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY="your-gemini-2.5-api-key"
```

---

## Quick Verification

To verify that the installation has succeeded and the Tree-sitter parsers are running correctly:
```bash
# Run unit tests
PYTHONPATH=. .venv/bin/pytest tests/test_scanner.py
```
If the tests pass, the environment is ready!

---

## Running Commands

Start by scanning the codebase:
```bash
# Document a project
python main.py document tests/dummy-project
```
Then, you can run requirements planning or code change audits:
```bash
# Plan a requirement
python main.py plan "Add billing address fields to customer model"

# Profile a function
python main.py analyze-function createUser
```
