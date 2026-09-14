#!/usr/bin/env bash
set -e
sudo pacman -S --needed python python-pip python-virtualenv traceroute iputils
cd "$(dirname "$0")/.."
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "VOID installation completed."
echo "Run with: ./run.sh"
