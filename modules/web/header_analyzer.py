from urllib.parse import urlparse

import requests
from rich.panel import Panel
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause

SECURITY_HEADERS = {
    "Strict-Transport-Security": "HSTS",
    "Content-Security-Policy": "CSP",
    "Content-Security-Policy-Report-Only": "CSP Report Only",
    "X-Frame-Options": "X-Frame-Options",
    "X-Content-Type-Options": "X-Content-Type-Options",
    "Referrer-Policy": "Referrer-Policy",
    "Permissions-Policy": "Permissions-Policy",
    "Cross-Origin-Opener-Policy": "COOP",
    "Cross-Origin-Embedder-Policy": "COEP",
    "Cross-Origin-Resource-Policy": "CORP",
}


def normalize_url(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value


def analyze_csp(value):
    warnings = []
    lowered = value.lower()
    if "'unsafe-inline'" in lowered:
        warnings.append("unsafe-inline")
    if "'unsafe-eval'" in lowered:
        warnings.append("unsafe-eval")
    if "default-src *" in lowered or "script-src *" in lowered:
        warnings.append("wildcard source")
    if "object-src" not in lowered:
        warnings.append("object-src missing")
    if "base-uri" not in lowered:
        warnings.append("base-uri missing")
    return warnings


def parse_set_cookie(headers):
    raw_values = []
    source = getattr(headers, "getlist", None)
    if callable(source):
        raw_values = source("Set-Cookie")
    if not raw_values:
        single = headers.get("Set-Cookie")
        if single:
            raw_values = [single]
    cookies = []
    for raw in raw_values:
        pieces = [piece.strip() for piece in raw.split(";") if piece.strip()]
        if not pieces:
            continue
        name = pieces[0].split("=", 1)[0]
        attributes = {piece.split("=", 1)[0].lower(): piece.split("=", 1)[1] if "=" in piece else True for piece in pieces[1:]}
        cookies.append({
            "name": name,
            "secure": "secure" in attributes,
            "httponly": "httponly" in attributes,
            "samesite": attributes.get("samesite"),
            "path": attributes.get("path"),
            "domain": attributes.get("domain"),
            "max_age": attributes.get("max-age"),
            "expires": attributes.get("expires"),
        })
    return cookies


def score_headers(headers, cookies, scheme):
    score = 0
    maximum = 10
    checks = {
        "HSTS": bool(headers.get("Strict-Transport-Security")) if scheme == "https" else False,
        "CSP": bool(headers.get("Content-Security-Policy")),
        "Frame Protection": bool(headers.get("X-Frame-Options") or "frame-ancestors" in headers.get("Content-Security-Policy", "").lower()),
        "MIME Sniffing Protection": headers.get("X-Content-Type-Options", "").lower() == "nosniff",
        "Referrer Policy": bool(headers.get("Referrer-Policy")),
        "Permissions Policy": bool(headers.get("Permissions-Policy")),
        "COOP": bool(headers.get("Cross-Origin-Opener-Policy")),
        "CORP": bool(headers.get("Cross-Origin-Resource-Policy")),
        "Secure Cookies": all(cookie["secure"] for cookie in cookies) if cookies else True,
        "HttpOnly Cookies": all(cookie["httponly"] for cookie in cookies) if cookies else True,
    }
    score = sum(1 for value in checks.values() if value)
    return score, maximum, checks


def run():
    module_header("Header Analyzer", "Web")
    target = normalize_url(console.input("[bold white]URL:[/bold white] "))

    try:
        response = requests.get(target, timeout=15, allow_redirects=True, headers={"User-Agent": "VOID/1.0"})
    except requests.RequestException as exc:
        console.print(f"[red]Request failed: {exc}[/red]")
        pause()
        return

    headers = response.headers
    parsed = urlparse(response.url)
    cookies = parse_set_cookie(response.raw.headers)
    score, maximum, checks = score_headers(headers, cookies, parsed.scheme)

    summary = Table(title="HTTP Response Summary", show_header=False, border_style="red")
    summary.add_column("Field", style="bold red")
    summary.add_column("Value", style="white")
    summary.add_row("Requested URL", target)
    summary.add_row("Final URL", response.url)
    summary.add_row("Status", f"{response.status_code} {response.reason}")
    summary.add_row("Protocol", f"HTTP/{response.raw.version / 10:.1f}" if response.raw.version else "Unknown")
    summary.add_row("Redirects", str(len(response.history)))
    summary.add_row("Content Type", headers.get("Content-Type", "Not provided"))
    summary.add_row("Content Length", headers.get("Content-Length", str(len(response.content))))
    summary.add_row("Server", headers.get("Server", "Not disclosed"))
    summary.add_row("Powered By", headers.get("X-Powered-By", "Not disclosed"))
    summary.add_row("Cache", headers.get("Cache-Control", "Not provided"))
    summary.add_row("ETag", headers.get("ETag", "Not provided"))
    summary.add_row("Age", headers.get("Age", "Not provided"))
    summary.add_row("Via", headers.get("Via", "Not provided"))
    console.print(summary)

    security = Table(title=f"Security Headers · Score {score}/{maximum}", border_style="red")
    security.add_column("Header", style="bold white")
    security.add_column("Status", style="bold")
    security.add_column("Value", style="white")
    for header, label in SECURITY_HEADERS.items():
        value = headers.get(header)
        status = "[green]Present[/green]" if value else "[red]Missing[/red]"
        security.add_row(label, status, value or "-")
    console.print(security)

    findings = []
    csp = headers.get("Content-Security-Policy")
    if csp:
        for warning in analyze_csp(csp):
            findings.append(f"CSP: {warning}")
    elif headers.get("Content-Security-Policy-Report-Only"):
        findings.append("CSP is report-only and is not enforcing policy")
    else:
        findings.append("Content-Security-Policy is missing")

    if parsed.scheme == "https" and not headers.get("Strict-Transport-Security"):
        findings.append("HSTS is missing on an HTTPS response")
    if headers.get("Access-Control-Allow-Origin") == "*":
        findings.append("CORS allows any origin")
    if headers.get("Access-Control-Allow-Credentials", "").lower() == "true" and headers.get("Access-Control-Allow-Origin") == "*":
        findings.append("CORS exposes credentials with a wildcard origin")
    if headers.get("Server"):
        findings.append("Server header discloses implementation information")
    if headers.get("X-Powered-By"):
        findings.append("X-Powered-By discloses technology information")

    cors = Table(title="CORS and Cross-Origin Policy", show_header=False, border_style="red")
    cors.add_column("Field", style="bold red")
    cors.add_column("Value", style="white")
    for key in [
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers",
        "Access-Control-Expose-Headers",
        "Cross-Origin-Opener-Policy",
        "Cross-Origin-Embedder-Policy",
        "Cross-Origin-Resource-Policy",
    ]:
        cors.add_row(key, headers.get(key, "Not provided"))
    console.print(cors)

    cookie_table = Table(title="Cookies", border_style="red")
    cookie_table.add_column("Name", style="bold white")
    cookie_table.add_column("Secure")
    cookie_table.add_column("HttpOnly")
    cookie_table.add_column("SameSite")
    cookie_table.add_column("Domain")
    cookie_table.add_column("Path")
    if cookies:
        for cookie in cookies:
            cookie_table.add_row(
                cookie["name"],
                "Yes" if cookie["secure"] else "No",
                "Yes" if cookie["httponly"] else "No",
                str(cookie["samesite"] or "Not set"),
                str(cookie["domain"] or "Host-only"),
                str(cookie["path"] or "Not set"),
            )
    else:
        cookie_table.add_row("No Set-Cookie headers", "-", "-", "-", "-", "-")
    console.print(cookie_table)

    redirect_lines = []
    for item in response.history:
        redirect_lines.append(f"{item.status_code} {item.url} -> {item.headers.get('Location', '')}")
    if redirect_lines:
        console.print(Panel("\n".join(redirect_lines), title="Redirect Chain", border_style="red"))

    if findings:
        console.print(Panel("\n".join(f"• {item}" for item in findings), title="Security Findings", border_style="yellow"))

    all_headers = {key: value for key, value in headers.items()}
    console.print(Panel("\n".join(f"{key}: {value}" for key, value in sorted(all_headers.items())), title="All Response Headers", border_style="red"))

    log_data = {
        "requested_url": target,
        "final_url": response.url,
        "status": response.status_code,
        "redirects": redirect_lines,
        "security_score": score,
        "security_checks": checks,
        "findings": findings,
        "cookies": cookies,
        "headers": all_headers,
    }
    path = save_log("header_analyzer", target, log_data)
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
