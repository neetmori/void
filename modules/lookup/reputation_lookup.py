import base64
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from rich.prompt import Prompt
from rich.table import Table

from core.config import BASE_DIR, CONFIG
from core.logger import save_log
from core.ui import console, module_header, pause
from core.validators import ensure_url, normalize_domain, valid_ip


def load_key():
    path = BASE_DIR / "api_keys.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("virustotal")
    except Exception:
        return None


def entity_id(kind, value):
    if kind == "URL":
        return base64.urlsafe_b64encode(value.encode("utf-8")).decode("ascii").strip("=")
    return value


def format_timestamp(value):
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).isoformat()
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def add_row(table, label, value):
    if value not in (None, "", [], {}):
        if isinstance(value, dict):
            value = ", ".join(f"{key}={item}" for key, item in value.items())
        elif isinstance(value, list):
            value = "\n".join(str(item) for item in value)
        table.add_row(label, str(value))


def run():
    module_header("Reputation Lookup", "OSINT")
    key = load_key()
    if not key:
        console.print("[yellow]VirusTotal API key is not configured.[/yellow]")
        console.print("[dim]Copy api_keys.json.example to api_keys.json and add your own key.[/dim]")
        pause()
        return

    kind = Prompt.ask("Type", choices=["IP", "DOMAIN", "URL", "HASH"], default="DOMAIN")
    value = Prompt.ask(kind).strip()
    endpoints = {"IP": "ip_addresses", "DOMAIN": "domains", "URL": "urls", "HASH": "files"}

    if kind == "IP" and not valid_ip(value):
        console.print("[red]Invalid IP address.[/red]")
        pause()
        return
    if kind == "DOMAIN":
        value = normalize_domain(value)
    if kind == "URL":
        value = ensure_url(value)

    identifier = entity_id(kind, value)
    url = f"https://www.virustotal.com/api/v3/{endpoints[kind]}/{identifier}"

    try:
        response = requests.get(url, headers={"x-apikey": key, "Accept": "application/json"}, timeout=CONFIG["request_timeout"])
        if response.status_code == 404:
            console.print("[yellow]No VirusTotal record was found for this target.[/yellow]")
            pause()
            return
        response.raise_for_status()
        envelope = response.json().get("data", {})
        data = envelope.get("attributes", {})
    except (requests.RequestException, ValueError) as exc:
        console.print(f"[red]Reputation lookup failed: {exc}[/red]")
        pause()
        return

    stats = data.get("last_analysis_stats") or {}
    results = data.get("last_analysis_results") or {}

    table = Table(title=f"VirusTotal Reputation · {kind}", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    add_row(table, "Target", value)
    add_row(table, "Reputation", data.get("reputation"))
    add_row(table, "Last Analysis", format_timestamp(data.get("last_analysis_date")))
    add_row(table, "First Submission", format_timestamp(data.get("first_submission_date")))
    add_row(table, "Last Submission", format_timestamp(data.get("last_submission_date")))
    add_row(table, "Last Modification", format_timestamp(data.get("last_modification_date")))
    add_row(table, "Times Submitted", data.get("times_submitted"))
    add_row(table, "Tags", data.get("tags"))
    add_row(table, "Categories", data.get("categories"))
    add_row(table, "Popular Threat Label", (data.get("popular_threat_classification") or {}).get("suggested_threat_label"))
    add_row(table, "Network", data.get("network"))
    add_row(table, "ASN", data.get("asn"))
    add_row(table, "AS Owner", data.get("as_owner"))
    add_row(table, "Country", data.get("country"))
    add_row(table, "Registrar", data.get("registrar"))
    add_row(table, "Creation Date", format_timestamp(data.get("creation_date")))
    add_row(table, "File Type", data.get("type_description"))
    add_row(table, "Meaningful Name", data.get("meaningful_name"))
    add_row(table, "MD5", data.get("md5"))
    add_row(table, "SHA-1", data.get("sha1"))
    add_row(table, "SHA-256", data.get("sha256"))
    add_row(table, "File Size", data.get("size"))
    console.print(table)

    stats_table = Table(title="Analysis Statistics", border_style="red")
    stats_table.add_column("Verdict", style="bold red")
    stats_table.add_column("Count", justify="right", style="white")
    for name in ["malicious", "suspicious", "harmless", "undetected", "timeout", "failure", "type-unsupported"]:
        if name in stats:
            stats_table.add_row(name.title(), str(stats[name]))
    if stats_table.row_count:
        console.print(stats_table)

    detections = []
    for engine, result in results.items():
        category = result.get("category")
        if category in {"malicious", "suspicious"}:
            detections.append({
                "engine": engine,
                "category": category,
                "result": result.get("result"),
                "method": result.get("method"),
            })

    if detections:
        detection_table = Table(title="Malicious or Suspicious Detections", border_style="red")
        detection_table.add_column("Engine", style="bold red")
        detection_table.add_column("Category")
        detection_table.add_column("Result", style="white")
        for item in detections[:100]:
            detection_table.add_row(item["engine"], str(item["category"]), str(item["result"] or ""))
        console.print(detection_table)

    path = save_log(
        "reputation_lookup",
        value,
        {
            "type": kind,
            "stats": stats,
            "detections": detections,
            "attributes": data,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
