# VOID Cybersecurity Framework

Made by unbeau.

VOID is a cross-platform terminal-based cybersecurity, OSINT, networking, web analysis, cryptography, file analysis and local testing toolkit.

## Quick start

```bash
python void.py
```

If your system exposes Python 3 as `python3`:

```bash
python3 void.py
```

On first launch, VOID checks its Python dependencies and attempts to install any missing packages automatically.

## Dependencies

VOID uses:

- rich
- requests
- dnspython
- Pillow
- phonenumbers

Manual installation:

```bash
python -m pip install -r requirements.txt
```

## Lookups and OSINT

- IP intelligence with address classification, reverse DNS and public network metadata
- ASN intelligence with organization, prefixes and BGP peer information
- RDAP lookup for domains, IP networks and ASNs
- Email intelligence using public DNS, Gravatar and optional official HIBP API access
- Public username profile lookup
- GitHub public-profile, repository, organization and activity lookup
- Certificate Transparency discovery
- Phone number parsing, validation, region, carrier and formatting metadata
- Reputation lookup for IPs, domains, URLs and file hashes through a user-supplied VirusTotal API key
- Public Gravatar profile lookup

Legacy WHOIS and MAC vendor lookup modules were removed. RDAP is used as the structured registration-data lookup.

## Network tools

- Reverse DNS with forward-confirmation checks
- Advanced DNS record inspection
- DNSSEC record and delegation inspection
- Bounded TCP port scanner
- IPv4 and IPv6 CIDR calculator
- Limited ping diagnostics
- Traceroute diagnostics

## Web tools

- HTTP response and latency diagnostics
- HTTP header, cookie, CORS, caching and security-policy analysis
- SSL/TLS certificate, cipher and protocol inspection
- robots.txt parsing
- Sitemap discovery
- URL parsing and normalization
- Bounded subdomain resolution
- Redirect-chain analysis
- Public technology fingerprinting
- Favicon MD5, SHA-1, SHA-256 and Shodan-compatible MMH3 fingerprints
- security.txt discovery and parsing

## Cryptography and encoding

- Hash format analysis
- Multi-algorithm hash generation
- Base64 and Base64URL encoding and decoding
- JWT structure and claim decoding without signature verification
- Password composition and entropy analysis

## File analysis

- Multi-algorithm file hashing and basic file metadata
- Image and EXIF metadata inspection, including GPS conversion when metadata is present

## Local testing and training

VOID contains local-only testing and deliberately constrained training modules. Remote authentication, credential extraction, remote command execution and remote flooding are intentionally excluded.

The HTTP load-testing module is restricted to loopback targets:

```text
localhost
127.0.0.1
::1
```

The training modules use localhost-only or synthetic workflows where applicable.

## Optional API keys

Copy:

```text
api_keys.json.example
```

to:

```text
api_keys.json
```

VirusTotal reputation lookup uses the `virustotal` key from that file.

Email breach exposure lookup can optionally use the official Have I Been Pwned API through the `HIBP_API_KEY` environment variable.

## Supported systems

VOID is designed for:

- Arch Linux and Arch-based distributions
- Debian
- Ubuntu
- Kali Linux
- Linux Mint
- Fedora and Fedora-based distributions
- macOS
- Windows

Some network modules use system utilities such as `ping`, `traceroute` or `tracert`.

### Arch Linux

```bash
sudo pacman -S python python-pip traceroute iputils
```

### Debian, Ubuntu, Kali and Linux Mint

```bash
sudo apt update
sudo apt install python3 python3-pip traceroute iputils-ping
```

### Fedora

```bash
sudo dnf install python3 python3-pip traceroute iputils
```

### macOS

```bash
brew install python
```

### Windows

Install Python 3, enable `Add Python to PATH`, open Command Prompt or PowerShell in the VOID directory and run:

```text
python void.py
```

## Optional installers

Prepared installers are available in:

```text
install/
```

Files:

```text
install_arch.sh
install_debian.sh
install_fedora.sh
install_macos.sh
install_windows.bat
```

## Virtual environment

Linux and macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python void.py
```

Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python void.py
```

## Project structure

```text
VOID/
├── void.py
├── config.json
├── requirements.txt
├── README.md
├── run.sh
├── run.bat
├── install/
├── core/
├── modules/
├── logs/
├── output/
└── wordlists/
```

## Configuration

General settings are stored in:

```text
config.json
```

VOID writes supported module results as JSON into:

```text
logs/
```

## Safety

Use networking, reconnaissance and web-analysis modules only on systems you own or have explicit authorization to test.

A defensive reference for developers is included at:

```text
docs/UNSAFE_FEATURES_TO_AVOID.md
```

## Credits

VOID Cybersecurity Framework

Made by unbeau.
