import base64
import json
from datetime import datetime, timezone

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def decode_segment(segment):
    padded = segment + "=" * ((4 - len(segment) % 4) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    return json.loads(raw.decode("utf-8"))


def format_timestamp(value):
    try:
        return datetime.fromtimestamp(float(value), timezone.utc).isoformat()
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def run():
    module_header("JWT Decoder", "Cryptography")
    token = console.input("[bold white]JWT:[/bold white] ").strip()
    parts = token.split(".")
    if len(parts) not in {2, 3}:
        console.print("[red]JWT must contain two or three Base64URL segments.[/red]")
        pause()
        return

    try:
        header = decode_segment(parts[0])
        payload = decode_segment(parts[1])
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, base64.binascii.Error) as exc:
        console.print(f"[red]JWT decoding failed: {exc}[/red]")
        pause()
        return

    signature = parts[2] if len(parts) == 3 else ""
    now = datetime.now(timezone.utc).timestamp()
    exp = payload.get("exp")
    nbf = payload.get("nbf")
    iat = payload.get("iat")

    summary = Table(title="JWT Summary", show_header=False, border_style="red")
    summary.add_column("Field", style="bold red")
    summary.add_column("Value", style="white")
    summary.add_row("Algorithm", str(header.get("alg") or "Not provided"))
    summary.add_row("Type", str(header.get("typ") or "Not provided"))
    summary.add_row("Key ID", str(header.get("kid") or "Not provided"))
    summary.add_row("Issuer", str(payload.get("iss") or "Not provided"))
    summary.add_row("Subject", str(payload.get("sub") or "Not provided"))
    summary.add_row("Audience", str(payload.get("aud") or "Not provided"))
    summary.add_row("Issued At", format_timestamp(iat) or str(iat or "Not provided"))
    summary.add_row("Not Before", format_timestamp(nbf) or str(nbf or "Not provided"))
    summary.add_row("Expires", format_timestamp(exp) or str(exp or "Not provided"))
    summary.add_row("Expired", str(float(exp) < now) if isinstance(exp, (int, float)) else "Unknown")
    summary.add_row("Currently Active", str((not isinstance(nbf, (int, float)) or float(nbf) <= now) and (not isinstance(exp, (int, float)) or float(exp) > now)))
    summary.add_row("Signature Present", str(bool(signature)))
    summary.add_row("Signature Verified", "No")
    console.print(summary)

    header_table = Table(title="JWT Header", border_style="red")
    header_table.add_column("Claim", style="bold red")
    header_table.add_column("Value", style="white")
    for key, value in header.items():
        header_table.add_row(str(key), json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value))
    console.print(header_table)

    payload_table = Table(title="JWT Payload", border_style="red")
    payload_table.add_column("Claim", style="bold red")
    payload_table.add_column("Value", style="white")
    for key, value in payload.items():
        payload_table.add_row(str(key), json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value))
    console.print(payload_table)

    findings = []
    if str(header.get("alg", "")).lower() == "none":
        findings.append("Token declares alg=none")
    if exp is None:
        findings.append("No expiration claim")
    if isinstance(exp, (int, float)) and float(exp) < now:
        findings.append("Token is expired")
    if isinstance(nbf, (int, float)) and float(nbf) > now:
        findings.append("Token is not active yet")

    path = save_log("jwt_decoder", "jwt", {"header": header, "payload": payload, "signature_present": bool(signature), "signature_verified": False, "findings": findings})
    if findings:
        console.print("[yellow]" + "\n".join(f"• {item}" for item in findings) + "[/yellow]")
    console.print("[dim]This tool decodes structure only and does not verify the JWT signature.[/dim]")
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
