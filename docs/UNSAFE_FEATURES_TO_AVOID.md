# Unsafe or invasive functionality to avoid

Made by unbeau.

This document is a defensive design reference for developers working on VOID. The entries below are intentionally non-operational. They describe categories of features that should not be implemented as general-purpose attack tooling.

## Do not add these as unrestricted modules

| Unsafe feature | Why to avoid it | Safe replacement |
|---|---|---|
| Credential stuffing | Attempts logins using reused credentials and can compromise accounts | Password strength checks, authentication auditing on local test fixtures |
| Password spraying | Tries common passwords across many accounts | Offline password-policy checks |
| Brute-force login automation | Repeated login attempts can cause account compromise or lockouts | Local mock-login rate-limit testing |
| Remote DDoS or flood tools | Can disrupt third-party services | Keep the existing localhost-only stress test |
| Botnet or distributed traffic control | Enables coordinated abuse | Local benchmark workers bound to localhost |
| Malware loaders or droppers | Delivers or executes malicious payloads | Static file/hash inspection |
| Reverse shells or persistent remote access | Creates unauthorized control channels | Local socket demos without remote command execution |
| Credential stealers | Extracts passwords, cookies or tokens | Browser/session security guidance only |
| Token or cookie hijacking | Enables account takeover | JWT decoding without signature bypass or theft |
| Phishing kit generators | Facilitates credential theft | Security-awareness templates without credential collection |
| Exploit automation against arbitrary hosts | Can directly compromise remote systems | Version detection and remediation guidance |
| SQL injection exploitation | Can extract or alter remote database data | Safe local training applications and defensive query checks |
| Mass vulnerability exploitation | Scales compromise across many targets | Non-invasive configuration and header checks |
| Stealth or evasion modules | Helps hide malicious behavior | Transparent logging and audit trails |
| Data exfiltration utilities | Moves stolen data out of a system | Local export of the user's own scan results |
| Email harvesting at scale | Enables spam and targeting | Domain-level mail infrastructure lookup |
| Private-person deanonymization | Invades privacy | Public technical metadata only |
| SIM-swap or telecom abuse tooling | Enables account takeover | Phone number format and carrier parsing only |
| API-key theft or secret scraping | Targets credentials | Local secret-scanning for the user's own repository |
| Keylogging or screen capture spyware | Collects private user data | None; exclude from the framework |

## Example of a module that should remain disabled

```text
UnsafeModule:
    status = DISABLED
    reason = "Would automate credential attacks against remote services"
    safe_alternative = "Local authentication test fixture"
```

## Design rule

A VOID module should normally be acceptable when it performs one of these actions:

- Parses data supplied by the user.
- Reads public technical metadata.
- Queries a documented public API.
- Analyzes the user's local files.
- Tests localhost or an explicitly local training environment.
- Performs limited network diagnostics for authorized systems.
- Produces defensive findings without exploiting them.

If a proposed feature attempts to obtain access, steal credentials, persist on another machine, evade detection, disrupt a remote service, or extract private data, it should not be included as a normal VOID module.
