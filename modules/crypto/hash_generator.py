import hashlib

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

ALGORITHMS = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_224", "sha3_256", "sha3_384", "sha3_512", "blake2b", "blake2s"]


def run():
    module_header("Hash Generator", "Cryptography")
    value = console.input("[bold white]Text:[/bold white] ")
    encoding = console.input("[bold white]Text encoding [utf-8]:[/bold white] ").strip() or "utf-8"
    try:
        data = value.encode(encoding)
    except (LookupError, UnicodeEncodeError) as exc:
        console.print(f"[red]Encoding failed: {exc}[/red]")
        pause()
        return

    digests = {}
    for algorithm in ALGORITHMS:
        digests[algorithm] = hashlib.new(algorithm, data).hexdigest()

    table = Table(title="Generated Digests", border_style="red")
    table.add_column("Algorithm", style="bold red")
    table.add_column("Digest", style="white")
    table.add_column("Bits", justify="right")
    for algorithm, digest in digests.items():
        table.add_row(algorithm.upper(), digest, str(len(digest) * 4))
    console.print(table)

    path = save_log("hash_generator", "text_input", {"encoding": encoding, "input_bytes": len(data), "digests": digests})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
