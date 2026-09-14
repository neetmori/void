import ipaddress
import re

import requests
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def detect_target(target):
    value = target.strip()
    if re.fullmatch(r"(?i)AS\d+", value):
        return "autnum", value[2:]
    if value.isdigit():
        return "autnum", value
    try:
        ipaddress.ip_address(value)
        return "ip", value
    except ValueError:
        return "domain", value.lower().rstrip(".")


def flatten_vcard(vcard):
    result = {}
    if not isinstance(vcard, list) or len(vcard) < 2:
        return result
    for item in vcard[1]:
        if not isinstance(item, list) or len(item) < 4:
            continue
        key = str(item[0])
        value = item[3]
        if isinstance(value, list):
            value = ", ".join(str(part) for part in value if part not in (None, ""))
        if value not in (None, ""):
            result.setdefault(key, []).append(str(value))
    return result


def extract_entities(entities, depth=0):
    rows = []
    if depth > 3:
        return rows
    for entity in entities or []:
        card = flatten_vcard(entity.get("vcardArray"))
        roles = entity.get("roles") or []
        rows.append({
            "handle": entity.get("handle"),
            "roles": roles,
            "name": (card.get("fn") or card.get("org") or [None])[0],
            "email": card.get("email") or [],
            "phone": card.get("tel") or [],
            "address": card.get("adr") or [],
            "links": [link.get("href") for link in entity.get("links", []) if link.get("href")],
            "public_ids": entity.get("publicIds") or [],
        })
        rows.extend(extract_entities(entity.get("entities"), depth + 1))
    return rows


def event_map(events):
    result = {}
    for event in events or []:
        action = event.get("eventAction")
        date = event.get("eventDate")
        if action and date:
            result.setdefault(action, []).append(date)
    return result


def fetch_rdap(kind, value):
    endpoint = {
        "domain": f"https://rdap.org/domain/{value}",
        "ip": f"https://rdap.org/ip/{value}",
        "autnum": f"https://rdap.org/autnum/{value}",
    }[kind]
    response = requests.get(endpoint, timeout=15, headers={"Accept": "application/rdap+json", "User-Agent": "VOID/1.0"})
    response.raise_for_status()
    return endpoint, response.json()


def add_row(table, label, value):
    if value not in (None, "", [], {}):
        if isinstance(value, list):
            value = "\n".join(str(item) for item in value)
        table.add_row(label, str(value))


def run():
    module_header("RDAP Lookup", "OSINT")
    target = console.input("[bold white]Domain, IP or ASN:[/bold white] ").strip()
    if not target:
        console.print("[red]Target is required.[/red]")
        pause()
        return

    kind, value = detect_target(target)
    try:
        endpoint, data = fetch_rdap(kind, value)
    except requests.RequestException as exc:
        console.print(f"[red]RDAP request failed: {exc}[/red]")
        pause()
        return
    except ValueError:
        console.print("[red]RDAP returned invalid JSON.[/red]")
        pause()
        return

    table = Table(title="RDAP Registration Data", show_header=False, border_style="red")
    table.add_column("Field", style="bold red", no_wrap=True)
    table.add_column("Value", style="white")

    add_row(table, "Target Type", kind.upper())
    add_row(table, "Query", target)
    add_row(table, "RDAP URL", endpoint)
    add_row(table, "Handle", data.get("handle"))
    add_row(table, "Name", data.get("ldhName") or data.get("unicodeName") or data.get("name"))
    add_row(table, "Unicode Name", data.get("unicodeName"))
    add_row(table, "Status", data.get("status"))
    add_row(table, "Port 43", data.get("port43"))
    add_row(table, "Country", data.get("country"))
    add_row(table, "Type", data.get("type"))
    add_row(table, "Start Address", data.get("startAddress"))
    add_row(table, "End Address", data.get("endAddress"))
    add_row(table, "IP Version", data.get("ipVersion"))
    add_row(table, "Parent Handle", data.get("parentHandle"))
    add_row(table, "Start ASN", data.get("startAutnum"))
    add_row(table, "End ASN", data.get("endAutnum"))

    events = event_map(data.get("events"))
    for action, dates in events.items():
        add_row(table, f"Event: {action}", dates)

    nameservers = []
    for item in data.get("nameservers") or []:
        name = item.get("ldhName") or item.get("unicodeName")
        addresses = item.get("ipAddresses") or {}
        parts = [name] if name else []
        parts.extend(addresses.get("v4") or [])
        parts.extend(addresses.get("v6") or [])
        if parts:
            nameservers.append(" | ".join(parts))
    add_row(table, "Nameservers", nameservers)

    secure_dns = data.get("secureDNS") or {}
    add_row(table, "DNSSEC Delegation Signed", secure_dns.get("delegationSigned"))
    add_row(table, "DNSSEC Zone Signed", secure_dns.get("zoneSigned"))
    ds_records = []
    for record in secure_dns.get("dsData") or []:
        ds_records.append(
            f"keyTag={record.get('keyTag')} algorithm={record.get('algorithm')} digestType={record.get('digestType')} digest={record.get('digest')}"
        )
    add_row(table, "DS Records", ds_records)

    entities = extract_entities(data.get("entities"))
    entity_lines = []
    for entity in entities:
        parts = []
        if entity.get("name"):
            parts.append(entity["name"])
        if entity.get("handle"):
            parts.append(f"handle={entity['handle']}")
        if entity.get("roles"):
            parts.append("roles=" + ",".join(entity["roles"]))
        if entity.get("email"):
            parts.append("email=" + ",".join(entity["email"]))
        if entity.get("phone"):
            parts.append("phone=" + ",".join(entity["phone"]))
        if parts:
            entity_lines.append(" | ".join(parts))
    add_row(table, "Entities", entity_lines)

    remarks = []
    for item in (data.get("remarks") or []) + (data.get("notices") or []):
        title = item.get("title")
        description = item.get("description") or []
        text = " ".join(description)
        if title or text:
            remarks.append(f"{title or 'Notice'}: {text}".strip())
    add_row(table, "Remarks / Notices", remarks)

    links = [item.get("href") for item in data.get("links", []) if item.get("href")]
    add_row(table, "Links", links)

    console.print(table)
    console.print(Panel("RDAP is the modern structured replacement for legacy WHOIS and may redact private registration data.", border_style="red"))

    log_data = {
        "target_type": kind,
        "endpoint": endpoint,
        "handle": data.get("handle"),
        "name": data.get("ldhName") or data.get("unicodeName") or data.get("name"),
        "status": data.get("status"),
        "events": events,
        "nameservers": nameservers,
        "secure_dns": secure_dns,
        "entities": entities,
        "remarks": remarks,
        "links": links,
        "raw": data,
    }
    path = save_log("rdap_lookup", target, log_data)
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
