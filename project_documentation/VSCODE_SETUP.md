# Visual Studio Code Setup Guide

This guide will help you set up and run the RAG-Powered Educational Content Generator project in Visual Studio Code.

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ **VS Code installed** - Download from [code.visualstudio.com](https://code.visualstudio.com/)
- ✅ **Python 3.9+ installed** - Download from [python.org](https://www.python.org/downloads/)
- ✅ **Poetry installed** - See [POETRY_SETUP.md](POETRY_SETUP.md) for installation
- ✅ **Git installed** (optional but recommended)

## 🚀 Step-by-Step Setup

### Step 1: Open Project in VS Code

1. **Open VS Code**
2. **Open the project folder:**
   - Click `File` → `Open Folder...`
   - Navigate to: `C:\Users\Linata04\Desktop\Semester 4\RAG-Powered Educational Content Generator`
   - Click "Select Folder"

   **OR** use Command Palette:
   - Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
   - Type "Open Folder"
   - Select the project folder

### Step 2: Install Recommended VS Code Extensions

VS Code will likely prompt you to install recommended extensions. Install these:

1. **Python Extension** (Microsoft)
   - Provides Python support, IntelliSense, debugging
   - Extension ID: `ms-python.python`

2. **Poetry Extension** (optional but helpful)
   - Better Poetry integration
   - Extension ID: `ms-python.poetry`

3. **Pylance** (usually comes with Python extension)
   - Advanced Python language server

**To install extensions:**
- Press `Ctrl+Shift+X` to open Extensions view
- Search for "Python" and install
- Search for "Poetry" and install

### Step 3: Configure Poetry

First, configure Poetry to create virtual environments in project directories:

```bash
# Open integrated terminal in VS Code: Ctrl+` (backtick) or View → Terminal
poetry config virtualenvs.in-project true
```

This ensures VS Code can easily find and use the virtual environments.

### Step 4: Set Up Backend

1. **Navigate to backend folder:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

   This will:
   - Create `backend/.venv` virtual environment
   - Install all dependencies from `pyproject.toml`

3. **Select Python Interpreter:**
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Select the Poetry virtual environment:
     - Should show: `.\backend\.venv\Scripts\python.exe` (Windows)
     - Or: `./backend/.venv/bin/python` (Linux/Mac)
   
   **Alternative:** Click on Python version in bottom-right status bar → Select interpreter

4. **Create `.env` file:**
   - In `backend` folder, create `.env` file (if it doesn't exist)
   - Add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=rag-educational-content
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   LOG_LEVEL=INFO
   EMBEDDING_MODEL=text-embedding-3-small
   LLM_MODEL=gpt-4-turbo-preview
   LLM_TEMPERATURE=0.7
   ```

### Step 5: Set Up Frontend

1. **Navigate to frontend folder:**
   ```bash
   cd ..\frontend
   # or on Linux/Mac: cd ../frontend
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

   This will:
   - Create `frontend/.venv` virtual environment
   - Install all dependencies

3. **Create `.env` file:**
   - In `frontend` folder, create `.env` file
   - Add:
   ```env
   BACKEND_API_URL=http://localhost:8000
   ```

### Step 6: Running the Application

#### Option A: Using VS Code Integrated Terminal

**Terminal 1 - Backend:**
```bash
cd backend
poetry run uvicorn rag_edu_generator.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
poetry run streamlit run src/streamlit_app/main.py
```

#### Option B: Using VS Code Tasks (Recommended)

We'll create tasks for easier running (see Step 7).

### Step 7: Configure VS Code Tasks (Optional but Recommended)

Create `.vscode/tasks.json` for easy running:

1. **Create `.vscode` folder** in project root (if it doesn't exist)

2. **Create `tasks.json`** with this content:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Backend: Start Server",
            "type": "shell",
            "command": "poetry",
            "args": [
                "run",
                "uvicorn",
                "rag_edu_generator.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "options": {
                "cwd": "${workspaceFolder}/backend"
            },
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "isBackground": true,
            "runOptions": {
                "runOn": "default"
            }
        },
        {
            "label": "Frontend: Start Streamlit",
            "type": "shell",
            "command": "poetry",
            "args": [
                "run",
                "streamlit",
                "run",
                "src/streamlit_app/main.py"
            ],
            "options": {
                "cwd": "${workspaceFolder}/frontend"
            },
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "isBackground": true,
            "runOptions": {
                "runOn": "default"
            }
        },
        {
            "label": "Start Both (Backend + Frontend)",
            "dependsOrder": "parallel",
            "dependsOn": [
                "Backend: Start Server",
                "Frontend: Start Streamlit"
            ],
            "problemMatcher": []
        }
    ]
}
```

**To use tasks:**
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Backend: Start Server" or "Frontend: Start Streamlit" or "Start Both"

### Step 8: Configure Debugging (Optional)

Create `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI Backend",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/backend/.venv/Scripts/uvicorn.exe",
            "args": [
                "rag_edu_generator.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "cwd": "${workspaceFolder}/backend",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/backend/src"
            },
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Python: Streamlit Frontend",
            "type": "debugpy",
            "request": "launch",
            "module": "streamlit",
            "args": [
                "run",
                "src/streamlit_app/main.py"
            ],
            "cwd": "${workspaceFolder}/frontend",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/frontend/src"
            },
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ],
    "compounds": [
        {
            "name": "Start Backend + Frontend",
            "configurations": [
                "Python: FastAPI Backend",
                "Python: Streamlit Frontend"
            ],
            "presentation": {
                "hidden": false,
                "group": "",
                "order": 1
            }
        }
    ]
}
```

**To debug:**
- Press `F5` or go to Run → Start Debugging
- Select configuration from dropdown
- Set breakpoints by clicking left of line numbers

### Step 9: Configure Workspace Settings (Recommended)

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.analysis.extraPaths": [
        "${workspaceFolder}/backend/src",
        "${workspaceFolder}/frontend/src"
    ],
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

### Step 10: Verify Setup

1. **Check Python Interpreter:**
   - Look at bottom-right corner of VS Code
   - Should show Python version from `.venv`
   - Click to change if needed

2. **Test Backend:**
   ```bash
   cd backend
   poetry run python -c "import fastapi; print('FastAPI installed!')"
   ```

3. **Test Frontend:**
   ```bash
   cd frontend
   poetry run python -c "import streamlit; print('Streamlit installed!')"
   ```

## 🎯 Quick Start Commands

### Running Backend
```bash
cd backend
poetry run uvicorn rag_edu_generator.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Frontend
```bash
cd frontend
poetry run streamlit run src/streamlit_app/main.py
```

### Using VS Code Tasks
- `Ctrl+Shift+P` → "Tasks: Run Task" → Select task

### Using Debugging
- Press `F5` → Select configuration

## 🔧 Useful VS Code Features

### Integrated Terminal
- **Open:** `Ctrl+` (backtick) or `View` → `Terminal`
- **Multiple terminals:** Click `+` icon or `Ctrl+Shift+` (backtick)
- **Split terminal:** Click split icon

### Command Palette
- **Open:** `Ctrl+Shift+P` or `F1`
- Quick access to all commands

### File Explorer
- **Open:** `Ctrl+Shift+E`
- Navigate project files easily

### Search
- **Search in files:** `Ctrl+Shift+F`
- **Search and replace:** `Ctrl+H`

### Git Integration
- Built-in Git support
- View changes, commit, push directly from VS Code

## 📁 Project Structure in VS Code

```
📁 RAG-Powered Educational Content Generator/
├── 📁 .vscode/              # VS Code configuration
│   ├── settings.json        # Workspace settings
│   ├── tasks.json           # Tasks for running apps
│   └── launch.json          # Debug configurations
├── 📁 backend/
│   ├── 📁 .venv/            # Poetry virtual environment
│   ├── pyproject.toml       # Poetry dependencies
│   ├── .env                 # Environment variables
│   └── 📁 src/
├── 📁 frontend/
│   ├── 📁 .venv/            # Poetry virtual environment
│   ├── pyproject.toml       # Poetry dependencies
│   ├── .env                 # Environment variables
│   └── 📁 src/
└── 📁 project_documentation/
```

## 🐛 Troubleshooting

### Python Interpreter Not Found

**Problem:** VS Code can't find Python interpreter

**Solution:**
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Select the Poetry virtual environment from `backend/.venv` or `frontend/.venv`

### Module Not Found Errors

**Problem:** Import errors like "ModuleNotFoundError: No module named 'rag_edu_generator'"

**Solution:**
1. Make sure you're using the correct virtual environment
2. Check `.vscode/settings.json` has correct `python.analysis.extraPaths`
3. Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"

### Poetry Command Not Found

**Problem:** "poetry: command not found"

**Solution:**
1. Install Poetry: See [POETRY_SETUP.md](POETRY_SETUP.md)
2. Make sure Poetry is in PATH
3. Restart VS Code terminal

### Port Already in Use

**Problem:** "Address already in use" when starting backend/frontend

**Solution:**
1. Find process using port:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   # Linux/Mac
   lsof -i :8000
   ```
2. Kill the process or change port in `.env`

### Environment Variables Not Loading

**Problem:** API keys not working

**Solution:**
1. Make sure `.env` files exist in `backend/` and `frontend/`
2. Check `.env` file syntax (no quotes around values)
3. Restart VS Code or reload window

## 💡 Tips for Better Experience

1. **Use Multiple Terminals:**
   - Run backend in one terminal
   - Run frontend in another
   - Keep them side-by-side

2. **Install Extensions:**
   - **Black Formatter** - Auto-format Python code
   - **Ruff** - Fast Python linter
   - **Python Docstring Generator** - Generate docstrings
   - **GitLens** - Enhanced Git capabilities

3. **Use IntelliSense:**
   - Hover over code for documentation
   - `Ctrl+Space` for autocomplete
   - `F12` to go to definition

4. **Debugging Tips:**
   - Set breakpoints by clicking left of line numbers
   - Use Debug Console to evaluate expressions
   - Step through code with F10 (step over) and F11 (step into)

5. **Git Integration:**
   - View file changes in Source Control panel
   - Commit directly from VS Code
   - Push/pull without leaving editor

## ✅ Checklist

- [ ] VS Code installed
- [ ] Python 3.9+ installed
- [ ] Poetry installed and configured
- [ ] Project opened in VS Code
- [ ] Python extension installed
- [ ] Backend dependencies installed (`poetry install` in backend/)
- [ ] Frontend dependencies installed (`poetry install` in frontend/)
- [ ] `.env` files created with API keys
- [ ] Python interpreter selected (from `.venv`)
- [ ] Backend runs successfully
- [ ] Frontend runs successfully
- [ ] VS Code tasks configured (optional)
- [ ] Debugging configured (optional)

## 🎉 You're All Set!

Your project is now configured in VS Code. You can:
- ✅ Edit code with full IntelliSense
- ✅ Run backend and frontend easily
- ✅ Debug your application
- ✅ Use Git integration
- ✅ Format code automatically

Happy coding! 🚀

---

*Last Updated: 2024*

