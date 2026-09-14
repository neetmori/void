MADE_BY = "Made by unbeau"

import hashlib
import os
import socket

import dns.resolver
import requests
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from core.ui import console, module_header, pause
from core.logger import save_log
from core.validators import valid_email


def _dns_values(domain, record_type):
    try:
        return [str(record).strip().strip('"') for record in dns.resolver.resolve(domain, record_type)]
    except Exception:
        return []


def _gravatar(email):
    digest = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    url = f"https://www.gravatar.com/avatar/{digest}?d=404"
    try:
        response = requests.get(url, timeout=6, allow_redirects=True)
        return response.status_code == 200, f"https://www.gravatar.com/avatar/{digest}"
    except requests.RequestException:
        return None, f"https://www.gravatar.com/avatar/{digest}"


def _hibp(email):
    """Optional breach-name lookup using the official HIBP API.

    Set HIBP_API_KEY in the environment to enable it. No passwords,
    hashes or private mailbox contents are requested or displayed.
    """
    api_key = os.getenv("HIBP_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        response = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            params={"truncateResponse": "true"},
            headers={
                "hibp-api-key": api_key,
                "user-agent": "VOID-public-email-osint",
            },
            timeout=8,
        )
        if response.status_code == 404:
            return []
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}"}
        return [item.get("Name", "Unknown") for item in response.json()]
    except (requests.RequestException, ValueError):
        return {"error": "Lookup failed"}


def run():
    module_header("EMAIL LOOKUP", "OSINT")
    email = Prompt.ask("[red]Email[/red]").strip()
    if not valid_email(email):
        console.print("[red]Invalid email format.[/red]")
        pause()
        return

    local, domain = email.rsplit("@", 1)
    domain = domain.lower()

    result = {
        "email": email,
        "local_part": local,
        "domain": domain,
        "domain_ips": [],
        "mx_records": [],
        "spf_records": [],
        "dmarc_records": [],
        "gravatar": None,
        "username_candidates": [],
        "breaches": None,
    }

    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="red")
    table.add_column("Value")
    table.add_row("Email", email)
    table.add_row("Local Part", local)
    table.add_row("Domain", domain)

    try:
        ips = socket.gethostbyname_ex(domain)[2]
        result["domain_ips"] = ips
        for ip in ips:
            table.add_row("Domain IP", ip)
    except Exception:
        table.add_row("Domain IP", "Not found")

    try:
        records = dns.resolver.resolve(domain, "MX")
        mx = [str(record.exchange).rstrip(".") for record in records]
        result["mx_records"] = mx
        for item in mx:
            table.add_row("MX", item)
    except Exception:
        table.add_row("MX", "Not found")

    txt_records = _dns_values(domain, "TXT")
    spf = [value for value in txt_records if value.lower().startswith("v=spf1")]
    result["spf_records"] = spf
    table.add_row("SPF", " | ".join(spf) if spf else "Not found")

    dmarc = _dns_values(f"_dmarc.{domain}", "TXT")
    dmarc = [value for value in dmarc if value.lower().startswith("v=dmarc1")]
    result["dmarc_records"] = dmarc
    table.add_row("DMARC", " | ".join(dmarc) if dmarc else "Not found")

    candidates = []
    for candidate in (
        local,
        local.replace(".", ""),
        local.replace("_", ""),
        local.replace("-", ""),
    ):
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    result["username_candidates"] = candidates
    table.add_row("Username candidates", ", ".join(candidates))

    gravatar_exists, gravatar_url = _gravatar(email)
    result["gravatar"] = {"exists": gravatar_exists, "url": gravatar_url}
    if gravatar_exists is True:
        table.add_row("Gravatar", f"Public avatar found: {gravatar_url}")
    elif gravatar_exists is False:
        table.add_row("Gravatar", "No public avatar found")
    else:
        table.add_row("Gravatar", "Lookup unavailable")

    breaches = _hibp(email)
    result["breaches"] = breaches
    if breaches is None:
        table.add_row("Breach exposure", "HIBP_API_KEY not configured")
    elif isinstance(breaches, dict):
        table.add_row("Breach exposure", breaches.get("error", "Lookup failed"))
    elif breaches:
        table.add_row("Breach exposure", ", ".join(breaches))
    else:
        table.add_row("Breach exposure", "No breach returned by HIBP")

    console.print(table)
    console.print(
        "\n[dim]Uses public DNS/Gravatar data and, when configured, the official "
        "Have I Been Pwned API. It does not access mailboxes, passwords, sessions, "
        "recovery codes or private account data.[/dim]"
    )
    save_log("email_lookup", email, result)
    pause()
