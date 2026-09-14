MADE_BY = "Made by unbeau"

import re
import ipaddress
from urllib.parse import urlparse

def normalize_domain(value):
    value = value.strip()
    if "://" in value:
        value = urlparse(value).hostname or value
    return value.split("/")[0].lower()

def valid_email(value):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))

def valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False

def ensure_url(value):
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value
