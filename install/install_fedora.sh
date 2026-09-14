#!/usr/bin/env bash
set -e
sudo dnf install -y python3 python3-pip traceroute iputils
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "VOID installation completed."
echo "Run with: ./run.sh"
