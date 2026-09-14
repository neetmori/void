import dns.exception
import dns.flags
import dns.resolver
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

RECORD_TYPES = [
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "NS",
    "SOA",
    "TXT",
    "CAA",
    "SRV",
    "NAPTR",
    "PTR",
    "HTTPS",
    "SVCB",
]


def query_record(resolver, domain, record_type):
    try:
        answer = resolver.resolve(domain, record_type, raise_on_no_answer=False, lifetime=5)
        values = [item.to_text() for item in answer]
        response = answer.response
        return {
            "values": values,
            "ttl": answer.rrset.ttl if answer.rrset else None,
            "authoritative": bool(response.flags & dns.flags.AA),
            "authenticated": bool(response.flags & dns.flags.AD),
            "truncated": bool(response.flags & dns.flags.TC),
            "rcode": response.rcode(),
        }
    except dns.resolver.NXDOMAIN:
        return {"error": "NXDOMAIN"}
    except dns.resolver.NoNameservers as exc:
        return {"error": f"No nameservers: {exc}"}
    except dns.resolver.LifetimeTimeout:
        return {"error": "Timeout"}
    except dns.exception.DNSException as exc:
        return {"error": str(exc)}


def run():
    module_header("Advanced DNS", "Network")
    domain = console.input("[bold white]Domain:[/bold white] ").strip().lower().rstrip(".")
    if not domain:
        console.print("[red]Domain is required.[/red]")
        pause()
        return

    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5

    results = {}
    table = Table(title=f"DNS Records · {domain}", border_style="red")
    table.add_column("Type", style="bold red", no_wrap=True)
    table.add_column("TTL", justify="right")
    table.add_column("Flags")
    table.add_column("Values", style="white")

    domain_exists = True
    for record_type in RECORD_TYPES:
        result = query_record(resolver, domain, record_type)
        results[record_type] = result
        if result.get("error") == "NXDOMAIN":
            domain_exists = False
            break
        values = result.get("values") or []
        if values:
            flags = []
            if result.get("authoritative"):
                flags.append("AA")
            if result.get("authenticated"):
                flags.append("AD")
            if result.get("truncated"):
                flags.append("TC")
            table.add_row(
                record_type,
                str(result.get("ttl") or "-"),
                ",".join(flags) or "-",
                "\n".join(values),
            )

    if not domain_exists:
        console.print(Panel("The domain does not exist according to DNS.", border_style="red"))
        path = save_log("advanced_dns", domain, results)
        console.print(f"[dim]Log saved to {path}[/dim]")
        pause()
        return

    if table.row_count:
        console.print(table)
    else:
        console.print(Panel("No supported DNS records were returned.", border_style="yellow"))

    resolver_table = Table(title="Resolver Context", show_header=False, border_style="red")
    resolver_table.add_column("Field", style="bold red")
    resolver_table.add_column("Value", style="white")
    resolver_table.add_row("Search Suffixes", ", ".join(str(item) for item in resolver.search) or "None")
    resolver_table.add_row("Nameservers", "\n".join(str(item) for item in resolver.nameservers))
    resolver_table.add_row("Timeout", str(resolver.timeout))
    resolver_table.add_row("Lifetime", str(resolver.lifetime))
    console.print(resolver_table)

    path = save_log("advanced_dns", domain, results)
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
