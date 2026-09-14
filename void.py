#!/usr/bin/env python3
MADE_BY = "Made by unbeau"

import importlib
import subprocess
import sys
import time

REQUIRED_PACKAGES = {
    "rich": "rich",
    "requests": "requests",
    "dns": "dnspython",
    "whois": "python-whois",
    "PIL": "Pillow",
    "phonenumbers": "phonenumbers",
}


def ensure_dependencies():
    missing = []
    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(package_name)

    if not missing:
        return

    print("VOID is preparing the required Python dependencies...")
    print("Missing packages:", ", ".join(missing))

    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            *missing,
        ])
    except subprocess.CalledProcessError:
        print()
        print("Automatic dependency installation failed.")
        print("Run this command manually:")
        print(f"{sys.executable} -m pip install " + " ".join(missing))
        sys.exit(1)


ensure_dependencies()

from rich.panel import Panel
from rich.prompt import Prompt
from core.ui import console, draw_header, menu_table

from modules.osint.ip_lookup import run as ip_lookup
from modules.osint.whois_lookup import run as whois_lookup
from modules.osint.email_lookup import run as email_lookup
from modules.osint.mac_lookup import run as mac_lookup

from modules.network.reverse_dns import run as reverse_dns
from modules.network.port_scanner import run as port_scanner
from modules.network.subnet_calc import run as subnet_calc
from modules.network.ping_monitor import run as ping_monitor
from modules.network.traceroute_tool import run as traceroute_tool

from modules.web.http_status import run as http_status
from modules.web.header_analyzer import run as header_analyzer
from modules.web.ssl_inspector import run as ssl_inspector
from modules.web.robots_analyzer import run as robots_analyzer
from modules.web.sitemap_finder import run as sitemap_finder
from modules.web.url_parser import run as url_parser
from modules.web.subdomain_resolver import run as subdomain_resolver
from modules.web.local_stress import run as local_stress

from modules.crypto.hash_analyzer import run as hash_analyzer
from modules.crypto.hash_generator import run as hash_generator
from modules.crypto.base64_tool import run as base64_tool
from modules.crypto.jwt_decoder import run as jwt_decoder
from modules.crypto.password_strength import run as password_strength

from modules.files.file_hash import run as file_hash
from modules.files.exif_viewer import run as exif_viewer
from modules.system.system_info import run as system_info

from modules.lookup.asn_lookup import run as asn_lookup
from modules.lookup.advanced_dns import run as advanced_dns
from modules.lookup.username_lookup import run as username_lookup
from modules.lookup.github_user_lookup import run as github_user_lookup
from modules.lookup.certificate_transparency import run as certificate_transparency
from modules.lookup.redirect_lookup import run as redirect_lookup
from modules.lookup.technology_lookup import run as technology_lookup
from modules.lookup.phone_parser import run as phone_parser
from modules.lookup.reputation_lookup import run as reputation_lookup
from modules.lookup.rdap_lookup import run as rdap_lookup
from modules.lookup.gravatar_lookup import run as gravatar_lookup
from modules.lookup.dnssec_lookup import run as dnssec_lookup
from modules.lookup.favicon_hash import run as favicon_hash
from modules.lookup.security_txt_lookup import run as security_txt_lookup

from modules.training.credential_stuffing_demo import run as credential_stuffing_demo
from modules.training.password_spraying_demo import run as password_spraying_demo
from modules.training.reverse_shell_demo import run as reverse_shell_demo
from modules.training.credential_stealer_demo import run as credential_stealer_demo
from modules.training.sqli_exploitation_demo import run as sqli_exploitation_demo
from modules.training.info_stealer_placeholder import run as info_stealer_placeholder


ROWS = [
    ("01", "Lookups & OSINT", "Category", "Public intelligence and identity lookups"),
    ("02", "Network", "Category", "DNS, ports, routing and subnet tools"),
    ("03", "Web", "Category", "HTTP, TLS and public website analysis"),
    ("04", "Cryptography", "Category", "Hashes, Base64, JWT and password analysis"),
    ("05", "File Analysis", "Category", "File hashes and EXIF metadata"),
    ("06", "Local Testing", "Category", "Localhost-only testing tools"),
    ("07", "System", "Category", "Local system information"),
    ("08", "Training / Disabled", "Category", "Non-operational training examples"),
    ("09", "Info Stealer", "Module", "Info Stealer menu entry"),
    ("00", "Exit", "System", "Close VOID"),
]


LOOKUP_ROWS = [
    ("01", "IP Lookup", "OSINT", "Public IP information"),
    ("02", "ASN Lookup", "OSINT", "ASN and organization information"),
    ("03", "WHOIS Lookup", "OSINT", "Domain registration metadata"),
    ("04", "Email Lookup", "OSINT", "Public email/domain intelligence"),
    ("05", "Username Lookup", "OSINT", "Public profile checks"),
    ("06", "GitHub User Lookup", "OSINT", "Public GitHub metadata"),
    ("07", "MAC Vendor Lookup", "OSINT", "MAC/OUI vendor information"),
    ("08", "Certificate Transparency", "OSINT", "Public certificate names"),
    ("09", "Phone Number Parser", "OSINT", "Parse public number metadata"),
    ("10", "Reputation Lookup", "OSINT", "Public reputation checks"),
    ("11", "RDAP Lookup", "OSINT", "Public registration data"),
    ("12", "Gravatar Lookup", "OSINT", "Public Gravatar metadata"),
    ("00", "Back", "System", "Return to main menu"),
]

LOOKUP_TOOLS = {
    "01": ip_lookup,
    "02": asn_lookup,
    "03": whois_lookup,
    "04": email_lookup,
    "05": username_lookup,
    "06": github_user_lookup,
    "07": mac_lookup,
    "08": certificate_transparency,
    "09": phone_parser,
    "10": reputation_lookup,
    "11": rdap_lookup,
    "12": gravatar_lookup,
}


NETWORK_ROWS = [
    ("01", "Reverse DNS", "Network", "Resolve IP to hostname"),
    ("02", "Advanced DNS", "Network", "A, AAAA, CNAME, MX, TXT, NS, SOA and CAA"),
    ("03", "DNSSEC Lookup", "Network", "DNSKEY and DS records"),
    ("04", "TCP Port Scanner", "Network", "Check selected TCP ports"),
    ("05", "CIDR Calculator", "Network", "Calculate subnet information"),
    ("06", "Ping Monitor", "Network", "Run a limited ping test"),
    ("07", "Traceroute", "Network", "Display network path"),
    ("00", "Back", "System", "Return to main menu"),
]

NETWORK_TOOLS = {
    "01": reverse_dns,
    "02": advanced_dns,
    "03": dnssec_lookup,
    "04": port_scanner,
    "05": subnet_calc,
    "06": ping_monitor,
    "07": traceroute_tool,
}


WEB_ROWS = [
    ("01", "HTTP Status Check", "Web", "Check HTTP response and latency"),
    ("02", "Header Analyzer", "Web", "Inspect HTTP security headers"),
    ("03", "SSL/TLS Inspector", "Web", "Inspect TLS certificate and cipher"),
    ("04", "robots.txt Analyzer", "Web", "Retrieve robots.txt"),
    ("05", "Sitemap Finder", "Web", "Check common sitemap locations"),
    ("06", "URL Parser", "Web", "Parse URL components"),
    ("07", "Subdomain Resolver", "Web", "Resolve a limited subdomain list"),
    ("08", "Redirect Lookup", "Web", "Display HTTP redirect chain"),
    ("09", "Technology Lookup", "Web", "Infer technologies from public signatures"),
    ("10", "Favicon Hash", "Web", "Calculate public favicon fingerprints"),
    ("11", "security.txt Lookup", "Web", "Retrieve published security contacts"),
    ("00", "Back", "System", "Return to main menu"),
]

WEB_TOOLS = {
    "01": http_status,
    "02": header_analyzer,
    "03": ssl_inspector,
    "04": robots_analyzer,
    "05": sitemap_finder,
    "06": url_parser,
    "07": subdomain_resolver,
    "08": redirect_lookup,
    "09": technology_lookup,
    "10": favicon_hash,
    "11": security_txt_lookup,
}


CRYPTO_ROWS = [
    ("01", "Hash Analyzer", "Crypto", "Identify common hash formats"),
    ("02", "Hash Generator", "Crypto", "Generate common hashes"),
    ("03", "Base64 Toolkit", "Encoding", "Encode and decode Base64"),
    ("04", "JWT Decoder", "Encoding", "Decode JWT header and payload"),
    ("05", "Password Strength", "Crypto", "Estimate password entropy"),
    ("00", "Back", "System", "Return to main menu"),
]

CRYPTO_TOOLS = {
    "01": hash_analyzer,
    "02": hash_generator,
    "03": base64_tool,
    "04": jwt_decoder,
    "05": password_strength,
}


FILE_ROWS = [
    ("01", "File Hash", "Files", "Calculate file checksums"),
    ("02", "EXIF Viewer", "Files", "Display image EXIF metadata"),
    ("00", "Back", "System", "Return to main menu"),
]

FILE_TOOLS = {
    "01": file_hash,
    "02": exif_viewer,
}


TRAINING_ROWS = [
    ("01", "Local Credential Test", "Local Only", "Credential workflow against localhost only"),
    ("02", "Local Password Spray", "Local Only", "Password iteration against localhost only"),
    ("03", "Mock Shell", "Local Only", "No sockets or OS command execution"),
    ("04", "Credential Storage Training", "Local Only", "Synthetic credentials only"),
    ("05", "Local SQL Training", "Local Only", "Local SQLite defensive query training"),
    ("00", "Back", "System", "Return to main menu"),
]

TRAINING_TOOLS = {
    "01": credential_stuffing_demo,
    "02": password_spraying_demo,
    "03": reverse_shell_demo,
    "04": credential_stealer_demo,
    "05": sqli_exploitation_demo,
}


def run_submenu(title, rows, tools):
    while True:
        draw_header()
        console.print(
            Panel(
                menu_table(rows),
                title=f"[bold white] VOID [/bold white][bold red]:: {title} ::[/bold red]",
                subtitle="[bold white]Made by unbeau[/bold white]",
                border_style="bright_red",
            )
        )
        option = Prompt.ask("\n[bold white]void[/bold white][bold red]@security[/bold red][bold white]:~$[/bold white]").strip().lower()
        if option in {"00", "back", "b"}:
            return

        function = tools.get(option)
        if function:
            try:
                function()
            except KeyboardInterrupt:
                console.print("\n[yellow]Operation cancelled.[/yellow]")
                time.sleep(1)
        else:
            console.print("[bold red][!] Unknown command.[/bold red]")
            time.sleep(1)


def main():
    while True:
        draw_header()
        console.print(
            Panel(
                menu_table(ROWS),
                title="[bold white] VOID [/bold white][bold red]:: TOOLKIT ::[/bold red]",
                subtitle="[bold white]Made by unbeau[/bold white]",
                border_style="bright_red",
            )
        )
        option = Prompt.ask("\n[bold white]void[/bold white][bold red]@security[/bold red][bold white]:~$[/bold white]").strip().lower()

        if option in {"00", "exit", "quit", "q"}:
            console.print("\n[bold white]VOID[/bold white] [red]session terminated.[/red]\n")
            return
        if option == "01":
            run_submenu("LOOKUPS & OSINT", LOOKUP_ROWS, LOOKUP_TOOLS)
        elif option == "02":
            run_submenu("NETWORK", NETWORK_ROWS, NETWORK_TOOLS)
        elif option == "03":
            run_submenu("WEB", WEB_ROWS, WEB_TOOLS)
        elif option == "04":
            run_submenu("CRYPTOGRAPHY", CRYPTO_ROWS, CRYPTO_TOOLS)
        elif option == "05":
            run_submenu("FILE ANALYSIS", FILE_ROWS, FILE_TOOLS)
        elif option == "06":
            local_stress()
        elif option == "07":
            system_info()
        elif option == "08":
            run_submenu("TRAINING / DISABLED", TRAINING_ROWS, TRAINING_TOOLS)
        elif option == "09":
            info_stealer_placeholder()
        else:
            console.print("[bold red][!] Unknown command.[/bold red]")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]VOID terminated.[/red]")
        sys.exit(0)
