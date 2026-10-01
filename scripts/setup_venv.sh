#!/bin/bash
set -e

# ==============================================================================
# GödelOS Virtual Environment Setup Script
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

VENV_DIR="godelos_venv"

echo "🧠 Initializing GödelOS Python Environment Setup..."

# Detect best available Python executable (prefer Python 3.10 - 3.12 for ML wheel stability)
PYTHON_EXE=""
for py in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$py" &>/dev/null; then
        PY_MAJOR=$("$py" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
        PY_MINOR=$("$py" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")
        if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 10 ] && [ "$PY_MINOR" -le 12 ]; then
            PYTHON_EXE="$py"
            break
        elif [ -z "$PYTHON_EXE" ] && [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 9 ]; then
            PYTHON_EXE="$py"
        fi
    fi
done

if [ -z "$PYTHON_EXE" ]; then
    echo "❌ Error: Python 3.9+ is required but could not be found."
    echo "Please install Python 3.10, 3.11, or 3.12."
    exit 1
fi

PY_VER=$("$PYTHON_EXE" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
TARGET_PY_MINOR=$("$PYTHON_EXE" -c "import sys; print(sys.version_info.minor)")
TARGET_PY_MM=$("$PYTHON_EXE" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

echo "✔ Using Python: $PYTHON_EXE (v$PY_VER)"

if [ "$TARGET_PY_MINOR" -ge 13 ]; then
    echo "⚠️  Note: Detected Python 3.13+. If you have Python 3.11 or 3.12 installed, using it is recommended for precompiled ML wheels."
fi

# Self-healing: check if existing venv is broken or built with a different Python version
if [ -d "$VENV_DIR" ]; then
    VENV_PY_VER=""
    if [ -x "$VENV_DIR/bin/python" ]; then
        VENV_PY_VER=$("$VENV_DIR/bin/python" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "")
    fi
    
    # Check if lib/pythonX.Y directory exists and matches
    if [ "$VENV_PY_VER" != "$TARGET_PY_MM" ] || [ ! -d "$VENV_DIR/lib/python$TARGET_PY_MM" ]; then
        echo "⚠️ Existing virtual environment in '$VENV_DIR' is corrupted or mismatched ($VENV_PY_VER vs target $TARGET_PY_MM)."
        echo "🧹 Removing stale virtual environment to ensure clean dependency resolution..."
        rm -rf "$VENV_DIR"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in '$VENV_DIR'..."
    "$PYTHON_EXE" -m venv "$VENV_DIR"
fi

if [ ! -d "$VENV_DIR" ] || [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "❌ Failed to create virtual environment in '$VENV_DIR'."
    exit 1
fi

VENV_PYTHON="$PROJECT_ROOT/$VENV_DIR/bin/python"

echo "Upgrading pip, setuptools, and wheel in virtual environment..."
"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel

echo "Installing project requirements from requirements.txt..."
"$VENV_PYTHON" -m pip install -r requirements.txt

if [ -f "backend/requirements.txt" ]; then
    echo "Installing backend requirements from backend/requirements.txt..."
    "$VENV_PYTHON" -m pip install -r backend/requirements.txt
fi

echo "Verifying core symbolic and backend package imports..."
"$VENV_PYTHON" - <<'PY'
import sys
core_packages = ['fastapi', 'uvicorn', 'pydantic', 'networkx']
missing = []
for p in core_packages:
    try:
        __import__(p)
    except ImportError:
        missing.append(p)

if missing:
    print(f"❌ Missing required core packages: {', '.join(missing)}")
    sys.exit(1)
print("✅ Core packages (fastapi, uvicorn, pydantic, networkx) successfully verified in virtual environment!")
PY

echo ""
echo "================================================================"
echo "🎉 Setup complete! The virtual environment '$VENV_DIR' is ready."
echo "================================================================"
echo ""
echo "To activate in your current shell:"
echo "    source $VENV_DIR/bin/activate"
echo "Or use the root helper:"
echo "    source ./venv"
