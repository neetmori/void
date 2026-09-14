#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
    echo "VOID is not installed yet."
    echo "Run the installer for your operating system inside the install/ folder."
    exit 1
fi
source .venv/bin/activate
python void.py
