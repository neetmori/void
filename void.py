MADE_BY = "Made by unbeau"

import importlib
import subprocess
import sys
import time

REQUIRED_PACKAGES = {
    "rich": "rich",
    "requests": "requests",
    "dns": "dnspython",
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
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
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
from modules.osint.email_lookup import run as email_lookup

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

from modules.crypto.hash_analyzer import run as hash_analyzer
from modules.crypto.hash_generator import run as hash_generator
from modules.crypto.base64_tool import run as base64_tool
from modules.crypto.jwt_decoder import run as jwt_decoder
from modules.crypto.password_strength import run as password_strength

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

from modules.training.info_stealer_placeholder import run as info_stealer_placeholder


ROWS = [
    ("01", "Lookups & OSINT", "Category", "Public intelligence and identity lookups"),
    ("02", "Network", "Category", "DNS, ports, routing and subnet tools"),
    ("03", "Web", "Category", "HTTP, TLS and public website analysis"),
    ("04", "Cryptography", "Category", "Hashes, Base64, JWT and password analysis"),
    ("05", "Info Stealer", "Module", "Disabled Info Stealer structure"),
    ("00", "Exit", "System", "Close VOID"),
]


LOOKUP_ROWS = [
    ("01", "IP Lookup", "OSINT", "Public IP intelligence"),
    ("02", "ASN Lookup", "OSINT", "ASN, prefix and organization information"),
    ("03", "RDAP Lookup", "OSINT", "Domain, IP and ASN registration data"),
    ("04", "Email Lookup", "OSINT", "Public email and domain intelligence"),
    ("05", "Username Lookup", "OSINT", "Public profile checks"),
    ("06", "GitHub User Lookup", "OSINT", "Public GitHub account metadata"),
    ("07", "Certificate Transparency", "OSINT", "Public certificate names and issuers"),
    ("08", "Phone Number Parser", "OSINT", "Number format, carrier and region metadata"),
    ("09", "Reputation Lookup", "OSINT", "Public reputation sources"),
    ("10", "Gravatar Lookup", "OSINT", "Public Gravatar profile metadata"),
    ("00", "Back", "System", "Return to main menu"),
]

LOOKUP_TOOLS = {
    "01": ip_lookup,
    "02": asn_lookup,
    "03": rdap_lookup,
    "04": email_lookup,
    "05": username_lookup,
    "06": github_user_lookup,
    "07": certificate_transparency,
    "08": phone_parser,
    "09": reputation_lookup,
    "10": gravatar_lookup,
}


NETWORK_ROWS = [
    ("01", "Reverse DNS", "Network", "Resolve IP addresses to hostnames"),
    ("02", "Advanced DNS", "Network", "Inspect public DNS record sets"),
    ("03", "DNSSEC Lookup", "Network", "Inspect DNSSEC records and delegation"),
    ("04", "TCP Port Scanner", "Network", "Check selected TCP ports"),
    ("05", "CIDR Calculator", "Network", "Calculate IPv4 and IPv6 subnet information"),
    ("06", "Ping Monitor", "Network", "Run a limited connectivity test"),
    ("07", "Traceroute", "Network", "Display the network path"),
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
    ("01", "HTTP Status Check", "Web", "Response, latency and redirect summary"),
    ("02", "Header Analyzer", "Web", "HTTP headers, cookies and security posture"),
    ("03", "SSL/TLS Inspector", "Web", "Certificate, protocol and cipher information"),
    ("04", "robots.txt Analyzer", "Web", "Retrieve and summarize robots.txt"),
    ("05", "Sitemap Finder", "Web", "Discover published sitemap locations"),
    ("06", "URL Parser", "Web", "Parse and normalize URL components"),
    ("07", "Subdomain Resolver", "Web", "Resolve a limited subdomain list"),
    ("08", "Redirect Lookup", "Web", "Display and classify redirect chains"),
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
    ("02", "Hash Generator", "Crypto", "Generate common cryptographic digests"),
    ("03", "Base64 Toolkit", "Encoding", "Encode and decode Base64"),
    ("04", "JWT Decoder", "Encoding", "Decode JWT header and payload"),
    ("05", "Password Strength", "Crypto", "Estimate password entropy and composition"),
    ("00", "Back", "System", "Return to main menu"),
]

CRYPTO_TOOLS = {
    "01": hash_analyzer,
    "02": hash_generator,
    "03": base64_tool,
    "04": jwt_decoder,
    "05": password_strength,
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
