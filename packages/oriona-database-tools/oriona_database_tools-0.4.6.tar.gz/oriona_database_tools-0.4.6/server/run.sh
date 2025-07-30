#!/bin/bash
set -e

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install dependencies if they don't exist
if [ ! -d "$DIR/venv" ]; then
    python3 -m venv "$DIR/venv" >/dev/null 2>&1
    "$DIR/venv/bin/pip" install --upgrade pip >/dev/null 2>&1
    "$DIR/venv/bin/pip" install -r "$DIR/../requirements.txt" >/dev/null 2>&1
fi

# Run the main script with the virtual environment
exec "$DIR/venv/bin/python" "$DIR/main.py" "$@"