MADE_BY = "Made by unbeau"

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"

LOG_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)
