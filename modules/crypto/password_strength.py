import math
import string
from collections import Counter

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

COMMON_PATTERNS = ["password", "qwerty", "123456", "admin", "letmein", "welcome", "abc123"]


def character_pool(value):
    pool = 0
    classes = {}
    classes["lowercase"] = any(char.islower() for char in value)
    classes["uppercase"] = any(char.isupper() for char in value)
    classes["digits"] = any(char.isdigit() for char in value)
    classes["symbols"] = any(char in string.punctuation or (not char.isalnum() and not char.isspace()) for char in value)
    classes["spaces"] = any(char.isspace() for char in value)
    if classes["lowercase"]:
        pool += 26
    if classes["uppercase"]:
        pool += 26
    if classes["digits"]:
        pool += 10
    if classes["symbols"]:
        pool += 33
    if classes["spaces"]:
        pool += 1
    return pool, classes


def shannon_entropy(value):
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values()) * length


def run():
    module_header("Password Strength", "Cryptography")
    value = console.input("[bold white]Password to analyze:[/bold white] ")
    if not value:
        console.print("[red]Password is required.[/red]")
        pause()
        return

    pool, classes = character_pool(value)
    theoretical_entropy = len(value) * math.log2(pool) if pool else 0.0
    observed_entropy = shannon_entropy(value)
    lower = value.lower()
    repeated = len(set(value)) < max(2, len(value) // 3)
    sequential = any(sequence in lower for sequence in ["0123456789", "123456789", "abcdefghijklmnopqrstuvwxyz", "qwertyuiop", "asdfghjkl"])
    common = any(pattern in lower for pattern in COMMON_PATTERNS)

    score = 0
    if len(value) >= 12:
        score += 2
    elif len(value) >= 8:
        score += 1
    score += min(sum(classes.values()), 4)
    if theoretical_entropy >= 80:
        score += 2
    elif theoretical_entropy >= 50:
        score += 1
    if common:
        score -= 2
    if sequential:
        score -= 1
    if repeated:
        score -= 1
    score = max(0, min(score, 8))
    rating = ["Very Weak", "Very Weak", "Weak", "Weak", "Fair", "Good", "Strong", "Very Strong", "Very Strong"][score]

    table = Table(title="Password Strength Analysis", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Length", str(len(value)))
    table.add_row("Unique Characters", str(len(set(value))))
    table.add_row("Character Pool", str(pool))
    table.add_row("Theoretical Entropy", f"{theoretical_entropy:.2f} bits")
    table.add_row("Observed Shannon Entropy", f"{observed_entropy:.2f} bits")
    table.add_row("Lowercase", str(classes["lowercase"]))
    table.add_row("Uppercase", str(classes["uppercase"]))
    table.add_row("Digits", str(classes["digits"]))
    table.add_row("Symbols", str(classes["symbols"]))
    table.add_row("Spaces", str(classes["spaces"]))
    table.add_row("Common Pattern", str(common))
    table.add_row("Sequential Pattern", str(sequential))
    table.add_row("Heavy Repetition", str(repeated))
    table.add_row("Rating", rating)
    console.print(table)

    recommendations = []
    if len(value) < 14:
        recommendations.append("Increase length to at least 14 characters")
    if sum(classes.values()) < 3:
        recommendations.append("Use a broader mix of character classes")
    if common or sequential:
        recommendations.append("Avoid common words and predictable sequences")
    if repeated:
        recommendations.append("Reduce repeated characters")
    if recommendations:
        console.print("[yellow]" + "\n".join(f"• {item}" for item in recommendations) + "[/yellow]")

    path = save_log(
        "password_strength",
        "local_input",
        {
            "length": len(value),
            "unique_characters": len(set(value)),
            "character_pool": pool,
            "theoretical_entropy_bits": theoretical_entropy,
            "observed_entropy_bits": observed_entropy,
            "classes": classes,
            "common_pattern": common,
            "sequential_pattern": sequential,
            "heavy_repetition": repeated,
            "rating": rating,
            "recommendations": recommendations,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
