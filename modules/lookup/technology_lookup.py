import re
from urllib.parse import urlparse

import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

SIGNATURES = {
    "WordPress": [r"wp-content", r"wp-includes"],
    "Drupal": [r"drupal-settings-json", r"sites/default/files"],
    "Joomla": [r"/media/system/js/", r"com_content"],
    "Shopify": [r"cdn\.shopify\.com", r"Shopify\.theme"],
    "Wix": [r"static\.wixstatic\.com", r"wix-code-sdk"],
    "Squarespace": [r"static1\.squarespace\.com", r"squarespace-cdn"],
    "Next.js": [r"/_next/", r"__NEXT_DATA__"],
    "Nuxt": [r"/_nuxt/", r"__NUXT__"],
    "React": [r"react-root", r"data-reactroot"],
    "Vue": [r"data-v-", r"__VUE__"],
    "Angular": [r"ng-version", r"ng-app"],
    "Bootstrap": [r"bootstrap(?:\.min)?\.(?:css|js)"],
    "Tailwind CSS": [r"tailwind", r"--tw-"],
    "jQuery": [r"jquery(?:-|\.)(?:min\.)?js", r"jQuery"],
    "Cloudflare": [r"cf-ray", r"cloudflare"],
}


def normalize_url(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def detect_from_body(body):
    detected = []
    for technology, patterns in SIGNATURES.items():
        if any(re.search(pattern, body, re.IGNORECASE) for pattern in patterns):
            detected.append(technology)
    return detected


def detect_headers(headers):
    detected = []
    server = headers.get("Server", "")
    powered = headers.get("X-Powered-By", "")
    generator = headers.get("X-Generator", "")
    combined = " ".join([server, powered, generator]).lower()
    mapping = {
        "nginx": "Nginx",
        "apache": "Apache HTTP Server",
        "iis": "Microsoft IIS",
        "express": "Express",
        "php": "PHP",
        "asp.net": "ASP.NET",
        "cloudflare": "Cloudflare",
        "gunicorn": "Gunicorn",
        "uvicorn": "Uvicorn",
    }
    for marker, name in mapping.items():
        if marker in combined:
            detected.append(name)
    return detected


def run():
    module_header("Technology Lookup", "Web")
    target = normalize_url(console.input("[bold white]URL:[/bold white] "))

    try:
        response = requests.get(target, timeout=15, allow_redirects=True, headers={"User-Agent": "VOID/1.0"})
        response.raise_for_status()
    except requests.RequestException as exc:
        console.print(f"[red]Technology lookup failed: {exc}[/red]")
        pause()
        return

    body = response.text[:2_000_000]
    detected = sorted(set(detect_from_body(body) + detect_headers(response.headers)))
    meta_generators = re.findall(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', body, re.IGNORECASE)
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)', body, re.IGNORECASE)
    styles = re.findall(r'<link[^>]+href=["\']([^"\']+\.css(?:\?[^"\']*)?)', body, re.IGNORECASE)

    host = urlparse(response.url).hostname or ""
    table = Table(title=f"Technology Fingerprint · {host}", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Final URL", response.url)
    table.add_row("Status", str(response.status_code))
    table.add_row("Server", response.headers.get("Server", "Not disclosed"))
    table.add_row("X-Powered-By", response.headers.get("X-Powered-By", "Not disclosed"))
    table.add_row("Generator", ", ".join(meta_generators) or "Not detected")
    table.add_row("Detected Technologies", ", ".join(detected) or "No known signatures detected")
    table.add_row("Script Resources", str(len(scripts)))
    table.add_row("Stylesheet Resources", str(len(styles)))
    table.add_row("CDN Indicator", "Cloudflare" if response.headers.get("CF-RAY") else response.headers.get("Via", "Not detected"))
    console.print(table)

    resource_table = Table(title="Public Resource Signatures", border_style="red")
    resource_table.add_column("Type", style="bold red")
    resource_table.add_column("URL", style="white")
    for value in scripts[:30]:
        resource_table.add_row("Script", value)
    for value in styles[:30]:
        resource_table.add_row("Stylesheet", value)
    if resource_table.row_count:
        console.print(resource_table)

    path = save_log(
        "technology_lookup",
        target,
        {
            "final_url": response.url,
            "headers": dict(response.headers),
            "detected": detected,
            "meta_generators": meta_generators,
            "scripts": scripts,
            "stylesheets": styles,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
