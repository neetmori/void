import posixpath
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlparse, urlunparse

from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def normalize_url(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    try:
        host_ascii = host.encode("idna").decode("ascii")
    except UnicodeError:
        host_ascii = host
    netloc = host_ascii
    if parsed.port:
        default_port = (parsed.scheme == "http" and parsed.port == 80) or (parsed.scheme == "https" and parsed.port == 443)
        if not default_port:
            netloc = f"{netloc}:{parsed.port}"
    path = parsed.path or "/"
    normalized_path = posixpath.normpath(path)
    if path.endswith("/") and not normalized_path.endswith("/"):
        normalized_path += "/"
    if not normalized_path.startswith("/"):
        normalized_path = "/" + normalized_path
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    normalized_query = urlencode(query_items, doseq=True)
    normalized = urlunparse((parsed.scheme.lower(), netloc, normalized_path, "", normalized_query, parsed.fragment))
    return parsed, normalized, query_items


def run():
    module_header("URL Parser", "Web")
    raw = console.input("[bold white]URL:[/bold white] ").strip()
    try:
        parsed, normalized, query_items = normalize_url(raw)
        port = parsed.port
    except ValueError as exc:
        console.print(f"[red]Invalid URL: {exc}[/red]")
        pause()
        return

    table = Table(title="URL Components", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Original", raw)
    table.add_row("Normalized", normalized)
    table.add_row("Scheme", parsed.scheme or "Not set")
    table.add_row("Username", parsed.username or "Not set")
    table.add_row("Password Present", "Yes" if parsed.password is not None else "No")
    table.add_row("Hostname", parsed.hostname or "Not set")
    table.add_row("Port", str(port or "Default"))
    table.add_row("Path", parsed.path or "/")
    table.add_row("Decoded Path", unquote(parsed.path or "/"))
    table.add_row("Parameters", parsed.params or "None")
    table.add_row("Query", parsed.query or "None")
    table.add_row("Fragment", parsed.fragment or "None")
    table.add_row("Netloc", parsed.netloc or "Not set")
    console.print(table)

    if query_items:
        query_table = Table(title="Query Parameters", border_style="red")
        query_table.add_column("Key", style="bold red")
        query_table.add_column("Value", style="white")
        for key, value in query_items:
            query_table.add_row(key, value)
        console.print(query_table)

    findings = []
    if parsed.username or parsed.password:
        findings.append("URL contains embedded user information")
    if parsed.scheme == "http":
        findings.append("URL uses cleartext HTTP")
    if parsed.fragment:
        findings.append("Fragment is client-side and is not normally sent to the server")
    if parsed.hostname:
        try:
            idn = parsed.hostname.encode("idna").decode("ascii")
            if idn != parsed.hostname.lower():
                findings.append(f"IDN hostname representation: {idn}")
        except UnicodeError:
            pass

    path = save_log(
        "url_parser",
        raw,
        {
            "normalized": normalized,
            "scheme": parsed.scheme,
            "hostname": parsed.hostname,
            "port": port,
            "path": parsed.path,
            "query_parameters": query_items,
            "fragment": parsed.fragment,
            "findings": findings,
        },
    )
    if findings:
        console.print("[yellow]" + "\n".join(f"• {item}" for item in findings) + "[/yellow]")
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
