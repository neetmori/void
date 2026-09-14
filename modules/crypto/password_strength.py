MADE_BY = "Made by unbeau"

import math
import string
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause

def run():
    module_header("PASSWORD STRENGTH ANALYZER", "Cryptography")
    password = Prompt.ask("[red]Password[/red]", password=True)
    pool = 0
    if any(c.islower() for c in password): pool += 26
    if any(c.isupper() for c in password): pool += 26
    if any(c.isdigit() for c in password): pool += 10
    if any(c in string.punctuation for c in password): pool += len(string.punctuation)
    entropy = len(password) * math.log2(pool) if pool else 0
    if entropy < 40: rating = "Weak"
    elif entropy < 60: rating = "Moderate"
    elif entropy < 80: rating = "Strong"
    else: rating = "Very Strong"
    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="red")
    table.add_column("Value")
    table.add_row("Length", str(len(password)))
    table.add_row("Estimated Entropy", f"{entropy:.1f} bits")
    table.add_row("Rating", rating)
    console.print(table)
    pause()
