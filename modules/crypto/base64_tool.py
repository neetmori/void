import base64
import binascii

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def pad_base64(value):
    return value + "=" * ((4 - len(value) % 4) % 4)


def run():
    module_header("Base64 Toolkit", "Cryptography")
    mode = console.input("[bold white]Mode [encode/decode]:[/bold white] ").strip().lower()
    value = console.input("[bold white]Value:[/bold white] ")

    if mode in {"encode", "e", "1"}:
        encoding = console.input("[bold white]Text encoding [utf-8]:[/bold white] ").strip() or "utf-8"
        try:
            raw = value.encode(encoding)
        except (LookupError, UnicodeEncodeError) as exc:
            console.print(f"[red]Encoding failed: {exc}[/red]")
            pause()
            return
        result = {
            "standard": base64.b64encode(raw).decode("ascii"),
            "urlsafe": base64.urlsafe_b64encode(raw).decode("ascii"),
            "input_bytes": len(raw),
            "encoding": encoding,
        }
        table = Table(title="Base64 Encodings", show_header=False, border_style="red")
        table.add_column("Field", style="bold red")
        table.add_column("Value", style="white")
        table.add_row("Standard", result["standard"])
        table.add_row("URL Safe", result["urlsafe"])
        table.add_row("Input Bytes", str(result["input_bytes"]))
        console.print(table)
        path = save_log("base64_tool", "encode", result)
    elif mode in {"decode", "d", "2"}:
        variant = console.input("[bold white]Variant [auto/standard/urlsafe]:[/bold white] ").strip().lower() or "auto"
        padded = pad_base64(value.strip())
        attempts = []
        decoders = []
        if variant in {"auto", "standard"}:
            decoders.append(("standard", lambda item: base64.b64decode(item, validate=True)))
        if variant in {"auto", "urlsafe"}:
            decoders.append(("urlsafe", base64.urlsafe_b64decode))

        decoded = None
        used = None
        for name, decoder in decoders:
            try:
                decoded = decoder(padded)
                used = name
                break
            except (binascii.Error, ValueError) as exc:
                attempts.append(f"{name}: {exc}")

        if decoded is None:
            console.print("[red]Invalid Base64 input.[/red]")
            pause()
            return

        try:
            text = decoded.decode("utf-8")
            utf8 = True
        except UnicodeDecodeError:
            text = decoded.hex()
            utf8 = False

        result = {
            "variant": used,
            "decoded_bytes": len(decoded),
            "utf8": utf8,
            "text": text if utf8 else None,
            "hex": decoded.hex(),
            "decode_attempts": attempts,
        }
        table = Table(title="Base64 Decoding", show_header=False, border_style="red")
        table.add_column("Field", style="bold red")
        table.add_column("Value", style="white")
        table.add_row("Variant", used or "Unknown")
        table.add_row("Decoded Bytes", str(len(decoded)))
        table.add_row("UTF-8 Text", text if utf8 else "Not valid UTF-8")
        table.add_row("Hex", decoded.hex())
        console.print(table)
        path = save_log("base64_tool", "decode", result)
    else:
        console.print("[red]Unknown mode.[/red]")
        pause()
        return

    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
