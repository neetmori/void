import hashlib
import mimetypes
from pathlib import Path

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

ALGORITHMS = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s"]


def calculate_hashes(path):
    hashers = {name: hashlib.new(name) for name in ALGORITHMS}
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            for hasher in hashers.values():
                hasher.update(chunk)
    return {name: hasher.hexdigest() for name, hasher in hashers.items()}


def run():
    module_header("File Hash", "Files")
    raw = console.input("[bold white]File path:[/bold white] ").strip().strip('"')
    path = Path(raw).expanduser()
    if not path.is_file():
        console.print("[red]File not found.[/red]")
        pause()
        return

    try:
        hashes = calculate_hashes(path)
        stat = path.stat()
    except OSError as exc:
        console.print(f"[red]Could not read file: {exc}[/red]")
        pause()
        return

    mime_type, encoding = mimetypes.guess_type(path.name)
    metadata = {
        "name": path.name,
        "path": str(path.resolve()),
        "size_bytes": stat.st_size,
        "extension": path.suffix.lower(),
        "mime_type": mime_type,
        "encoding": encoding,
        "modified": stat.st_mtime,
        "created": stat.st_ctime,
        "mode": oct(stat.st_mode),
    }

    info = Table(title="File Metadata", show_header=False, border_style="red")
    info.add_column("Field", style="bold red")
    info.add_column("Value", style="white")
    for key, value in metadata.items():
        info.add_row(key.replace("_", " ").title(), str(value if value not in (None, "") else "Unknown"))
    console.print(info)

    table = Table(title="Cryptographic Digests", border_style="red")
    table.add_column("Algorithm", style="bold red")
    table.add_column("Digest", style="white")
    for name, digest in hashes.items():
        table.add_row(name.upper(), digest)
    console.print(table)

    log_path = save_log("file_hash", str(path.resolve()), {"metadata": metadata, "hashes": hashes})
    console.print(f"[dim]Log saved to {log_path}[/dim]")
    pause()
