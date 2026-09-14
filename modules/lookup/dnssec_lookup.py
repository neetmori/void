import dns.dnssec
import dns.exception
import dns.name
import dns.resolver
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def resolve_text(resolver, name, record_type):
    try:
        answer = resolver.resolve(name, record_type, raise_on_no_answer=False, lifetime=6)
        return [item.to_text() for item in answer], answer.rrset.ttl if answer.rrset else None
    except dns.exception.DNSException:
        return [], None


def parent_domain(domain):
    name = dns.name.from_text(domain)
    if len(name.labels) <= 2:
        return "."
    return name.parent().to_text().rstrip(".") or "."


def run():
    module_header("DNSSEC Lookup", "Network")
    domain = console.input("[bold white]Domain:[/bold white] ").strip().lower().rstrip(".")
    if not domain:
        console.print("[red]Domain is required.[/red]")
        pause()
        return

    resolver = dns.resolver.Resolver()
    resolver.use_edns(edns=0, ednsflags=dns.flags.DO, payload=1232)

    records = {}
    for record_type in ["DNSKEY", "DS", "RRSIG", "NSEC", "NSEC3", "CDS", "CDNSKEY"]:
        values, ttl = resolve_text(resolver, domain, record_type)
        records[record_type] = {"values": values, "ttl": ttl}

    parent = parent_domain(domain)
    parent_ds, parent_ds_ttl = resolve_text(resolver, domain, "DS")
    records["PARENT_DS"] = {"values": parent_ds, "ttl": parent_ds_ttl, "parent": parent}

    table = Table(title=f"DNSSEC · {domain}", border_style="red")
    table.add_column("Record", style="bold red")
    table.add_column("TTL", justify="right")
    table.add_column("Values", style="white")
    for record_type, data in records.items():
        if data.get("values"):
            table.add_row(record_type, str(data.get("ttl") or "-"), "\n".join(data["values"]))

    if table.row_count:
        console.print(table)
    else:
        console.print(Panel("No DNSSEC records were returned for this name.", border_style="yellow"))

    key_details = []
    for item in records["DNSKEY"]["values"]:
        parts = item.split()
        if len(parts) >= 4:
            flags, protocol, algorithm = parts[:3]
            role = "Key Signing Key" if flags == "257" else "Zone Signing Key" if flags == "256" else "Other"
            key_details.append(f"flags={flags} role={role} protocol={protocol} algorithm={algorithm}")

    ds_details = []
    for item in records["DS"]["values"]:
        parts = item.split()
        if len(parts) >= 4:
            ds_details.append(f"key_tag={parts[0]} algorithm={parts[1]} digest_type={parts[2]} digest={parts[3]}")

    status = Table(title="DNSSEC Summary", show_header=False, border_style="red")
    status.add_column("Field", style="bold red")
    status.add_column("Value", style="white")
    status.add_row("DNSKEY Present", "Yes" if records["DNSKEY"]["values"] else "No")
    status.add_row("DS Present", "Yes" if records["DS"]["values"] else "No")
    status.add_row("RRSIG Present", "Yes" if records["RRSIG"]["values"] else "No")
    status.add_row("Denial of Existence", "NSEC3" if records["NSEC3"]["values"] else "NSEC" if records["NSEC"]["values"] else "Not observed")
    status.add_row("CDS Present", "Yes" if records["CDS"]["values"] else "No")
    status.add_row("CDNSKEY Present", "Yes" if records["CDNSKEY"]["values"] else "No")
    status.add_row("Delegation Parent", parent)
    if key_details:
        status.add_row("DNSKEY Details", "\n".join(key_details))
    if ds_details:
        status.add_row("DS Details", "\n".join(ds_details))
    console.print(status)

    path = save_log("dnssec_lookup", domain, {"records": records, "key_details": key_details, "ds_details": ds_details})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
