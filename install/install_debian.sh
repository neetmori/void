#!/usr/bin/env bash
set -e
sudo apt update
sudo apt install -y python3 python3-pip python3-venv traceroute iputils-ping
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "VOID installation completed."
echo "Run with: ./run.sh"
