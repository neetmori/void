import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def run():
    module_header("Phone Number Parser", "OSINT")
    raw = console.input("[bold white]Phone number:[/bold white] ").strip()
    region = console.input("[bold white]Default region code if needed (for example BR, optional):[/bold white] ").strip().upper() or None

    try:
        number = phonenumbers.parse(raw, region)
    except phonenumbers.NumberParseException as exc:
        console.print(f"[red]Could not parse number: {exc}[/red]")
        pause()
        return

    possible = phonenumbers.is_possible_number(number)
    valid = phonenumbers.is_valid_number(number)
    number_type = phonenumbers.number_type(number)
    type_names = {
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "UAN",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
    }

    formats = {
        "E164": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164),
        "International": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        "National": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL),
        "RFC3966": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.RFC3966),
    }
    country_code = number.country_code
    national_number = number.national_number
    region_code = phonenumbers.region_code_for_number(number)
    description = geocoder.description_for_number(number, "en")
    operator = carrier.name_for_number(number, "en")
    timezones = timezone.time_zones_for_number(number)

    table = Table(title="Phone Number Metadata", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    table.add_row("Possible", str(possible))
    table.add_row("Valid", str(valid))
    table.add_row("Type", type_names.get(number_type, str(number_type)))
    table.add_row("Country Calling Code", f"+{country_code}")
    table.add_row("Region Code", str(region_code or "Unknown"))
    table.add_row("National Number", str(national_number))
    table.add_row("Geographic Description", description or "Unknown")
    table.add_row("Carrier", operator or "Unknown")
    table.add_row("Time Zones", ", ".join(timezones) or "Unknown")
    for label, value in formats.items():
        table.add_row(label, value)
    console.print(table)

    path = save_log(
        "phone_parser",
        raw,
        {
            "possible": possible,
            "valid": valid,
            "type": type_names.get(number_type, str(number_type)),
            "country_calling_code": country_code,
            "region_code": region_code,
            "national_number": national_number,
            "geographic_description": description,
            "carrier": operator,
            "timezones": list(timezones),
            "formats": formats,
        },
    )
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
