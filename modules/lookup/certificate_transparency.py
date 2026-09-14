import requests
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def run():
    module_header("Certificate Transparency", "OSINT")
    domain = console.input("[bold white]Domain:[/bold white] ").strip().lower().rstrip(".")
    if not domain:
        console.print("[red]Domain is required.[/red]")
        pause()
        return

    try:
        response = requests.get(
            "https://crt.sh/",
            params={"q": f"%.{domain}", "output": "json"},
            timeout=20,
            headers={"User-Agent": "VOID/1.0"},
        )
        response.raise_for_status()
        records = response.json()
    except (requests.RequestException, ValueError) as exc:
        console.print(f"[red]Certificate Transparency lookup failed: {exc}[/red]")
        pause()
        return

    names = set()
    issuers = set()
    normalized = []
    seen = set()
    for item in records:
        for field in ("name_value", "common_name"):
            for name in str(item.get(field) or "").splitlines():
                name = name.strip().lower().rstrip(".")
                if name:
                    names.add(name)
        issuer = str(item.get("issuer_name") or "").strip()
        if issuer:
            issuers.add(issuer)
        key = (item.get("id"), item.get("serial_number"), item.get("not_before"), item.get("not_after"))
        if key in seen:
            continue
        seen.add(key)
        normalized.append({
            "id": item.get("id"),
            "issuer": issuer,
            "common_name": item.get("common_name"),
            "names": str(item.get("name_value") or "").splitlines(),
            "not_before": item.get("not_before"),
            "not_after": item.get("not_after"),
            "serial_number": item.get("serial_number"),
            "entry_timestamp": item.get("entry_timestamp"),
        })

    summary = Table(title=f"Certificate Transparency · {domain}", show_header=False, border_style="red")
    summary.add_column("Field", style="bold red")
    summary.add_column("Value", style="white")
    summary.add_row("Unique DNS Names", str(len(names)))
    summary.add_row("Unique Issuers", str(len(issuers)))
    summary.add_row("Certificate Entries", str(len(normalized)))
    console.print(summary)

    name_table = Table(title="Observed DNS Names", border_style="red")
    name_table.add_column("DNS Name", style="white")
    for name in sorted(names)[:300]:
        name_table.add_row(name)
    if name_table.row_count:
        console.print(name_table)
    if len(names) > 300:
        console.print(Panel(f"{len(names) - 300} additional names were saved to the log.", border_style="yellow"))

    certificate_table = Table(title="Recent Certificate Entries", border_style="red")
    certificate_table.add_column("ID", style="bold red")
    certificate_table.add_column("Common Name")
    certificate_table.add_column("Issuer")
    certificate_table.add_column("Not Before")
    certificate_table.add_column("Not After")
    for item in normalized[:100]:
        certificate_table.add_row(
            str(item.get("id") or ""),
            str(item.get("common_name") or ""),
            str(item.get("issuer") or ""),
            str(item.get("not_before") or ""),
            str(item.get("not_after") or ""),
        )
    if certificate_table.row_count:
        console.print(certificate_table)

    path = save_log(
        "certificate_transparency",
        domain,
        {"dns_names": sorted(names), "issuers": sorted(issuers), "certificates": normalized},
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
