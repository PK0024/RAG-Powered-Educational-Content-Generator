# Poetry Setup Guide

This project uses **Poetry** for dependency management. Poetry is already configured with `pyproject.toml` files in both backend and frontend.

## 📦 About Poetry

Poetry is a modern dependency management tool for Python that:
- Manages dependencies declaratively in `pyproject.toml`
- Locks versions in `poetry.lock` for reproducible builds
- Handles virtual environments automatically
- Provides better dependency resolution than pip

## 🔧 Poetry and Virtual Environments

### How Poetry Handles Virtual Environments

**By default, Poetry creates virtual environments in a centralized location:**
- Windows: `C:\Users\YourUsername\AppData\Local\pypoetry\Cache\virtualenvs\`
- Linux/Mac: `~/.cache/pypoetry/virtualenvs/`

**However, you can configure Poetry to create `.venv` in your project directory** (recommended for this project):

```bash
poetry config virtualenvs.in-project true
```

This will:
- Create `.venv` folder in each project directory (backend/.venv, frontend/.venv)
- Make it easier to find and manage virtual environments
- Allow IDEs to automatically detect the virtual environment

### Using Existing `.venv`

If you already have a `.venv` folder:
1. Poetry can use it if you activate it first, OR
2. Delete the existing `.venv` and let Poetry create a new one (recommended)

**Recommended approach:**
```bash
# In backend/ or frontend/ directory
# Remove existing .venv if you want Poetry to manage it
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows PowerShell
Remove-Item -Recurse -Force .venv  # Windows PowerShell (alternative)

# Then let Poetry create and manage it
poetry install
```

## 🚀 Setup Steps

### Step 1: Configure Poetry (Optional but Recommended)

```bash
# Make Poetry create .venv in project directories
poetry config virtualenvs.in-project true

# Verify the setting
poetry config virtualenvs.in-project
# Should output: true
```

### Step 2: Backend Setup

```bash
cd backend

# Install all dependencies (creates .venv if it doesn't exist)
poetry install

# Activate the virtual environment (optional - poetry run handles this)
poetry shell

# Or run commands directly with poetry run
poetry run python -m uvicorn rag_edu_generator.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup

```bash
cd frontend

# Install all dependencies (creates .venv if it doesn't exist)
poetry install

# Run Streamlit
poetry run streamlit run src/streamlit_app/main.py
```

## 📝 Common Poetry Commands

### Installing Dependencies

```bash
# Install all dependencies from pyproject.toml
poetry install

# Install a new dependency
poetry add package-name

# Install a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Update a specific package
poetry update package-name
```

### Running Commands

```bash
# Run a command in the Poetry environment
poetry run python script.py
poetry run uvicorn ...
poetry run streamlit run ...

# Activate the shell (then run commands directly)
poetry shell
```

### Managing Virtual Environments

```bash
# Show virtual environment info
poetry env info

# Show virtual environment path
poetry env info --path

# Remove virtual environment
poetry env remove python

# List all virtual environments for this project
poetry env list
```

### Adding/Removing Dependencies

```bash
# Add a dependency
poetry add fastapi  # Will add to [tool.poetry.dependencies]

# Add a dev dependency
poetry add --group dev pytest

# Remove a dependency
poetry remove package-name

# Show installed packages
poetry show

# Show dependency tree
poetry show --tree
```

## 🔄 Migration from pip to Poetry

If you're currently using pip with requirements.txt:

1. **The project already has `pyproject.toml` files**, so Poetry is ready to use
2. **You can remove `requirements.txt` files** (they're optional now)
3. **Use Poetry commands instead:**
   - `pip install -r requirements.txt` → `poetry install`
   - `pip install package` → `poetry add package`
   - `python script.py` → `poetry run python script.py`

## ⚙️ Project Structure with Poetry

```
RAG-Powered Educational Content Generator/
├── backend/
│   ├── .venv/              # Poetry creates this (if configured)
│   ├── pyproject.toml      # Poetry configuration
│   ├── poetry.lock         # Locked dependency versions (generated)
│   └── src/...
├── frontend/
│   ├── .venv/              # Poetry creates this (if configured)
│   ├── pyproject.toml      # Poetry configuration
│   ├── poetry.lock         # Locked dependency versions (generated)
│   └── src/...
```

## 🎯 Benefits of Using Poetry

1. **Better Dependency Resolution**: Handles conflicting dependencies intelligently
2. **Lock File**: `poetry.lock` ensures everyone gets the same versions
3. **Declarative Configuration**: All dependencies in one `pyproject.toml` file
4. **Virtual Environment Management**: Automatic creation and management
5. **Separate Environments**: Backend and frontend have their own isolated environments
6. **Development Dependencies**: Easy separation of dev and production dependencies

## 🔍 Troubleshooting

### Poetry can't find Python

If you get errors about Python not being found:

```bash
# Tell Poetry which Python to use
poetry env use python3.11
# or
poetry env use C:\Python311\python.exe
```

### Virtual environment not in project directory

```bash
# Configure Poetry to create .venv in project
poetry config virtualenvs.in-project true

# Remove old virtual environment
poetry env remove python

# Reinstall
poetry install
```

### Want to use existing .venv

If you want to use an existing `.venv`:

1. Activate it manually: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
2. Poetry will detect it if it's activated
3. But it's better to let Poetry manage it

## 📚 Quick Reference

| Task | Poetry Command |
|------|---------------|
| Install dependencies | `poetry install` |
| Add dependency | `poetry add package-name` |
| Add dev dependency | `poetry add --group dev package-name` |
| Remove dependency | `poetry remove package-name` |
| Update dependencies | `poetry update` |
| Run command | `poetry run command` |
| Activate shell | `poetry shell` |
| Show dependencies | `poetry show` |
| Show env info | `poetry env info` |

## ✅ Summary

**Your project is already configured for Poetry!** Just use:

```bash
# Backend
cd backend
poetry install
poetry run uvicorn rag_edu_generator.main:app --reload

# Frontend
cd frontend
poetry install
poetry run streamlit run src/streamlit_app/main.py
```

The `.venv` folders will be created automatically by Poetry (if configured with `virtualenvs.in-project true`), or you can let Poetry use its default location. Either way, Poetry manages everything for you!

---

*Last Updated: 2024*

