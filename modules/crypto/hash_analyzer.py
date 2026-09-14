import math
import re
from collections import Counter

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

PATTERNS = [
    ("MD5", re.compile(r"^[a-fA-F0-9]{32}$")),
    ("SHA-1", re.compile(r"^[a-fA-F0-9]{40}$")),
    ("SHA-224", re.compile(r"^[a-fA-F0-9]{56}$")),
    ("SHA-256", re.compile(r"^[a-fA-F0-9]{64}$")),
    ("SHA-384", re.compile(r"^[a-fA-F0-9]{96}$")),
    ("SHA-512", re.compile(r"^[a-fA-F0-9]{128}$")),
    ("Bcrypt", re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$")),
    ("Argon2", re.compile(r"^\$argon2(?:id|i|d)\$")),
    ("scrypt", re.compile(r"^\$scrypt\$")),
    ("PBKDF2-SHA256", re.compile(r"^(?:pbkdf2_sha256\$|\$pbkdf2-sha256\$)")),
    ("NTLM or MD4-compatible hex", re.compile(r"^[a-fA-F0-9]{32}$")),
]


def shannon_entropy(value):
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def run():
    module_header("Hash Analyzer", "Cryptography")
    value = console.input("[bold white]Hash or encoded value:[/bold white] ").strip()
    if not value:
        console.print("[red]Value is required.[/red]")
        pause()
        return

    matches = []
    for name, pattern in PATTERNS:
        if pattern.search(value):
            matches.append(name)

    is_hex = bool(re.fullmatch(r"[a-fA-F0-9]+", value))
    unique_chars = len(set(value))
    entropy_per_character = shannon_entropy(value)
    total_estimated_entropy = entropy_per_character * len(value)

    table = Table(title="Hash Format Analysis", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Length", str(len(value)))
    table.add_row("Hexadecimal", str(is_hex))
    table.add_row("Unique Characters", str(unique_chars))
    table.add_row("Shannon Entropy / Character", f"{entropy_per_character:.4f} bits")
    table.add_row("Estimated Total Entropy", f"{total_estimated_entropy:.2f} bits")
    table.add_row("Likely Formats", "\n".join(matches) if matches else "Unknown or unsupported format")
    if value.startswith("$"):
        table.add_row("Structured Prefix", value.split("$", 3)[1] if len(value.split("$")) > 1 else value)
    console.print(table)

    path = save_log(
        "hash_analyzer",
        "input",
        {
            "length": len(value),
            "hexadecimal": is_hex,
            "unique_characters": unique_chars,
            "entropy_per_character": entropy_per_character,
            "estimated_total_entropy": total_estimated_entropy,
            "likely_formats": matches,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
