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
PY_MINOR=$("$PYTHON_EXE" -c "import sys; print(sys.version_info.minor)")

echo "✔ Using Python: $PYTHON_EXE (v$PY_VER)"

if [ "$PY_MINOR" -ge 13 ]; then
    echo "⚠️  Note: Detected Python 3.13+. If you have Python 3.11 or 3.12 installed, using it is recommended for precompiled ML wheels."
fi

echo "Creating virtual environment in '$VENV_DIR'..."
"$PYTHON_EXE" -m venv "$VENV_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Failed to create virtual environment in '$VENV_DIR'."
    exit 1
fi

echo "Activating '$VENV_DIR'..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "Installing project requirements from requirements.txt..."
pip install -r requirements.txt

if [ -f "backend/requirements.txt" ]; then
    echo "Installing backend requirements from backend/requirements.txt..."
    pip install -r backend/requirements.txt
fi

echo "Verifying core symbolic and backend package imports..."
python - <<'PY'
import sys
core_packages = ['fastapi', 'pydantic', 'networkx']
missing = []
for p in core_packages:
    try:
        __import__(p)
    except ImportError:
        missing.append(p)

if missing:
    print(f"❌ Missing required core packages: {', '.join(missing)}")
    sys.exit(1)
print("✅ Core packages successfully verified in virtual environment!")
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
