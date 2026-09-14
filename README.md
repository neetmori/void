# VOID Cybersecurity Framework

Made by unbeau.

VOID is a cross-platform terminal-based cybersecurity, OSINT, networking, web analysis, cryptography, file analysis and local testing toolkit.

## Quick start

The recommended way to run VOID is the same on every operating system:

```bash
python void.py
```

On systems where Python 3 is exposed as `python3`, use:

```bash
python3 void.py
```

On the first run, VOID automatically checks the Python dependencies it needs and installs any missing packages.

After that, run the same command again whenever you want to open VOID:

```bash
python void.py
```

## GitHub usage

After cloning the repository:

```bash
git clone <repository-url>
cd VOID
python void.py
```

If your system uses `python3`:

```bash
git clone <repository-url>
cd VOID
python3 void.py
```

## Automatic dependency setup

VOID checks for these Python packages automatically:

- rich
- requests
- dnspython
- python-whois
- Pillow

If one or more packages are missing, VOID attempts to install them with the same Python interpreter used to launch the framework.

Example:

```bash
python void.py
```

Internally, missing dependencies are installed using:

```bash
python -m pip install ...
```

If automatic installation is blocked by your operating system, use one of the fallback installation methods below.

## Features

- IP lookup
- Reverse DNS
- DNS lookup
- DNS A, AAAA, MX, TXT and NS lookup
- WHOIS lookup
- Email domain lookup
- TCP port scanner
- CIDR and subnet calculator
- Ping monitor
- Traceroute
- MAC vendor lookup
- HTTP status checker
- HTTP security header analyzer
- SSL/TLS inspector
- robots.txt analyzer
- sitemap finder
- URL parser
- subdomain resolver
- JWT decoder
- Hash analyzer
- Hash generator
- File hash calculator
- Base64 encoder and decoder
- Password strength analyzer
- EXIF metadata viewer
- Local-only HTTP stress test
- System information
- JSON logging

## Supported systems

VOID is designed to run on:

- Arch Linux and Arch-based distributions
- Debian
- Ubuntu
- Kali Linux
- Linux Mint
- Fedora and Fedora-based distributions
- macOS
- Windows

The primary launch command remains:

```bash
python void.py
```

or:

```bash
python3 void.py
```

## System tools

Some modules use operating-system utilities such as `ping` and `traceroute`.

If one of these tools is unavailable, install it using your operating system package manager.

### Arch Linux

```bash
sudo pacman -S python python-pip traceroute iputils
```

### Debian / Ubuntu / Kali / Linux Mint

```bash
sudo apt update
sudo apt install python3 python3-pip traceroute iputils-ping
```

### Fedora

```bash
sudo dnf install python3 python3-pip traceroute iputils
```

### macOS

Install Python 3 if necessary:

```bash
brew install python
```

`ping` and `traceroute` are normally already available on macOS.

### Windows

Install Python 3 and enable:

```text
Add Python to PATH
```

Then open Command Prompt or PowerShell inside the VOID folder and run:

```text
python void.py
```

## Fallback installers

VOID still includes optional installation scripts inside:

```text
install/
```

Available scripts:

```text
install_arch.sh
install_debian.sh
install_fedora.sh
install_macos.sh
install_windows.bat
```

These are optional. They are only needed if you prefer a prepared virtual environment or if automatic dependency setup does not work on your system.

## Optional virtual environment

You can also create a virtual environment manually.

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
│   ├── install_arch.sh
│   ├── install_debian.sh
│   ├── install_fedora.sh
│   ├── install_macos.sh
│   └── install_windows.bat
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

You can change:

- request timeout
- port scan timeout
- default TCP ports
- local stress-test request limit
- built-in subdomain list

## Logs

Modules that support logging write JSON files to:

```text
logs/
```

## Safety

Use networking, reconnaissance and web-analysis modules only on systems you own or have explicit authorization to test.

The HTTP stress-test module is intentionally restricted to:

```text
localhost
127.0.0.1
::1
```

It cannot be used by VOID to send its load test to arbitrary remote hosts.


## Lookup and OSINT expansion

VOID now includes an expanded lookup layer with:

- ASN lookup
- Combined domain lookup
- Advanced DNS lookup
- Email-domain MX/SPF/DMARC lookup
- Username lookup across a small set of public profile pages
- GitHub public-user lookup
- Certificate Transparency lookup
- Redirect-chain lookup
- Public technology fingerprint lookup
- Phone number parser
- Reputation lookup for IPs, domains, URLs and file hashes through a user-supplied VirusTotal API key

Reputation lookups are optional. Copy:

```text
api_keys.json.example
```

to:

```text
api_keys.json
```

and insert your own API key.

## Unsafe features reference

A defensive reference for developers is included at:

```text
docs/UNSAFE_FEATURES_TO_AVOID.md
```

It contains non-operational examples of invasive or abusive features that should not be added to VOID, together with safer replacements.


## Training / Disabled section

VOID now includes a visible training section containing deliberately non-operational examples of unsafe capabilities.

Included demonstrations:

- Credential stuffing flow
- Password spraying flow
- Remote flood flow
- Reverse-shell flow
- Credential-stealer flow
- SQL injection exploitation flow

These modules do not perform remote authentication, remote flooding, command execution, credential extraction, exploit payload generation or remote data extraction. They exist only to show developers what categories of behavior should remain excluded from production modules.

## Additional OSINT modules

The lookup section also includes:

- RDAP lookup
- Public Gravatar profile lookup
- DNSSEC lookup
- Favicon hash lookup
- security.txt lookup

All of these operate on public metadata or user-supplied inputs.


## Local-only training modules

The training modules are complete enough to demonstrate their workflows, but they are intentionally constrained to safe local environments.

Remote-target restrictions:

```text
localhost
127.0.0.1
::1
```

The credential-testing and load-testing modules reject non-loopback targets.

The mock-shell module does not create sockets and does not execute operating-system commands.

The credential-storage demo works only with synthetic data generated by VOID.

The SQL training module uses a local SQLite database and parameterized queries.

These restrictions are part of the security design and should not be removed.

## Credits

VOID Cybersecurity Framework

Made by unbeau.