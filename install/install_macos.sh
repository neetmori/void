#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found."
    echo "Install it from https://www.python.org/ or with Homebrew: brew install python"
    exit 1
fi
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "VOID installation completed."
echo "Run with: ./run.sh"
