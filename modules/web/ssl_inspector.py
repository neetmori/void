import hashlib
import socket
import ssl
from datetime import datetime, timezone

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def flatten_name(entries):
    result = {}
    for group in entries or []:
        for key, value in group:
            result.setdefault(key, []).append(value)
    return result


def run():
    module_header("SSL/TLS Inspector", "Web")
    host = console.input("[bold white]Hostname:[/bold white] ").strip().lower().rstrip(".")
    port_raw = console.input("[bold white]Port [443]:[/bold white] ").strip()
    try:
        port = int(port_raw or "443")
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        console.print("[red]Invalid port.[/red]")
        pause()
        return

    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=10) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
                certificate = tls_socket.getpeercert()
                binary_certificate = tls_socket.getpeercert(binary_form=True)
                cipher = tls_socket.cipher()
                protocol = tls_socket.version()
                alpn = tls_socket.selected_alpn_protocol()
                compression = tls_socket.compression()
    except (OSError, ssl.SSLError) as exc:
        console.print(f"[red]TLS connection failed: {exc}[/red]")
        pause()
        return

    subject = flatten_name(certificate.get("subject"))
    issuer = flatten_name(certificate.get("issuer"))
    sans = [value for kind, value in certificate.get("subjectAltName", []) if kind in {"DNS", "IP Address"}]
    not_before = certificate.get("notBefore")
    not_after = certificate.get("notAfter")
    expires_at = datetime.fromtimestamp(ssl.cert_time_to_seconds(not_after), timezone.utc) if not_after else None
    starts_at = datetime.fromtimestamp(ssl.cert_time_to_seconds(not_before), timezone.utc) if not_before else None
    remaining = (expires_at - datetime.now(timezone.utc)).days if expires_at else None
    fingerprint = hashlib.sha256(binary_certificate).hexdigest().upper()

    table = Table(title=f"TLS Inspection · {host}:{port}", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("TLS Protocol", str(protocol or "Unknown"))
    table.add_row("Cipher", str(cipher[0] if cipher else "Unknown"))
    table.add_row("Cipher Protocol", str(cipher[1] if cipher else "Unknown"))
    table.add_row("Cipher Bits", str(cipher[2] if cipher else "Unknown"))
    table.add_row("ALPN", str(alpn or "Not negotiated"))
    table.add_row("Compression", str(compression or "None"))
    table.add_row("Certificate Version", str(certificate.get("version") or "Unknown"))
    table.add_row("Serial Number", str(certificate.get("serialNumber") or "Unknown"))
    table.add_row("Subject CN", ", ".join(subject.get("commonName", [])) or "Not present")
    table.add_row("Subject Organization", ", ".join(subject.get("organizationName", [])) or "Not present")
    table.add_row("Issuer CN", ", ".join(issuer.get("commonName", [])) or "Not present")
    table.add_row("Issuer Organization", ", ".join(issuer.get("organizationName", [])) or "Not present")
    table.add_row("Valid From", starts_at.isoformat() if starts_at else "Unknown")
    table.add_row("Valid Until", expires_at.isoformat() if expires_at else "Unknown")
    table.add_row("Days Remaining", str(remaining) if remaining is not None else "Unknown")
    table.add_row("SHA-256 Fingerprint", fingerprint)
    table.add_row("SAN Count", str(len(sans)))
    table.add_row("OCSP Endpoints", "\n".join(certificate.get("OCSP", [])) or "Not published")
    table.add_row("CA Issuers", "\n".join(certificate.get("caIssuers", [])) or "Not published")
    table.add_row("CRL Distribution Points", "\n".join(certificate.get("crlDistributionPoints", [])) or "Not published")
    console.print(table)

    if sans:
        san_table = Table(title="Subject Alternative Names", border_style="red")
        san_table.add_column("Name", style="white")
        for value in sans[:300]:
            san_table.add_row(value)
        console.print(san_table)

    log_data = {
        "host": host,
        "port": port,
        "protocol": protocol,
        "cipher": cipher,
        "alpn": alpn,
        "compression": compression,
        "subject": subject,
        "issuer": issuer,
        "sans": sans,
        "valid_from": starts_at.isoformat() if starts_at else None,
        "valid_until": expires_at.isoformat() if expires_at else None,
        "days_remaining": remaining,
        "fingerprint_sha256": fingerprint,
        "certificate": certificate,
    }
    path = save_log("ssl_inspector", f"{host}:{port}", log_data)
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
