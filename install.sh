#!/usr/bin/env bash
# ==============================================================================
# Desktop Pet Ecosystem - Cross-Platform Installer for Linux & macOS
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "🐾 Installing Desktop Pet Ecosystem (Linux / macOS)"
echo "=========================================================="

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "❌ Error: python3 is not installed. Please install Python 3.8+."
    exit 1
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Found Python $PYTHON_VER"

# Check Tkinter
if ! python3 -c "import tkinter" &>/dev/null; then
    echo "⚠️ Warning: python3-tk does not appear to be installed."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "👉 On Debian/Ubuntu run: sudo apt install python3-tk python3-pip"
        echo "👉 On Fedora/RHEL run:   sudo dnf install python3-tkinter"
        echo "👉 On Arch Linux run:    sudo pacman -S tk"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "👉 On macOS run:         brew install python-tk"
    fi
fi

# Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv || {
        echo "⚠️ Could not create virtual environment. Installing with user-level pip..."
    }
fi

if [ -f ".venv/bin/pip" ]; then
    echo "📦 Installing dependencies into .venv..."
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
else
    echo "📦 Installing dependencies via pip..."
    pip3 install --user -r requirements.txt
fi

chmod +x run.sh || true

# Optional Linux desktop entry
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    DESKTOP_DIR="$HOME/.local/share/applications"
    if [ -d "$DESKTOP_DIR" ]; then
        DESKTOP_FILE="$DESKTOP_DIR/desktop-pet.desktop"
        cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=Desktop Pet Ecosystem
Comment=Physics-based interactive desktop pet overlay
Exec=bash -c "cd '$SCRIPT_DIR' && ./run.sh"
Terminal=false
Categories=Utility;Amusement;
StartupNotify=false
EOF
        chmod +x "$DESKTOP_FILE"
        echo "✓ Created application entry: $DESKTOP_FILE"
    fi
fi

echo "=========================================================="
echo "🎉 Installation complete! Launch anytime by running:"
echo "   ./run.sh"
echo "=========================================================="
