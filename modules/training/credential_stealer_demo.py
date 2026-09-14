MADE_BY = "Made by unbeau"

import json
from pathlib import Path
from core.ui import console, module_header, pause

SAMPLE_DATA = {
    "browser": "VOID Training Browser",
    "accounts": [
        {"site": "example.local", "username": "training-user", "password": "ExamplePassword1"}
    ],
    "tokens": [
        {"service": "example.local", "token": "training-token"}
    ]
}

def run():
    module_header("CREDENTIAL STORAGE TRAINING", "Training / Local Only")
    path = Path("output/training_credentials.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(SAMPLE_DATA, indent=2), encoding="utf-8")
    console.print(f"[green]Created synthetic training dataset:[/green] {path}")
    console.print("[dim]No browser databases, cookies, tokens or private keys are accessed.[/dim]")
    pause()
