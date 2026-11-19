#!/usr/bin/env bash
# ==============================================================================
# Desktop Pet Ecosystem - Launcher Script (Linux & macOS)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Prefer virtual environment python if present
if [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PY_BIN="$SCRIPT_DIR/.venv/bin/python3"
elif [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PY_BIN="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PY_BIN="python3"
else
    PY_BIN="python"
fi

# Run detached in background without holding open terminal
nohup "$PY_BIN" "$SCRIPT_DIR/desktop_spider.py" "$@" >/dev/null 2>&1 &
PID=$!

echo "🐾 Desktop Pet Ecosystem started in background (PID: $PID)."
