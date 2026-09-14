MADE_BY = "Made by unbeau"

import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from core.ui import console, module_header, pause

def run():
    module_header("PHONE NUMBER PARSER", "OSINT / Lookup")
    value = Prompt.ask("[red]Phone number with country code[/red]").strip()
    try:
        number = phonenumbers.parse(value, None)
        result = {
            "Valid": phonenumbers.is_valid_number(number),
            "Possible": phonenumbers.is_possible_number(number),
            "Country/Region": geocoder.description_for_number(number, "en") or "-",
            "Carrier": carrier.name_for_number(number, "en") or "-",
            "Timezones": ", ".join(timezone.time_zones_for_number(number)),
            "International": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "E164": phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        }
        table = Table(box=box.SIMPLE)
        table.add_column("Field", style="red")
        table.add_column("Value")
        for k, v in result.items():
            table.add_row(k, str(v))
        console.print(table)
        console.print("\n[dim]This parser does not identify a private owner.[/dim]")
    except Exception as e:
        console.print(f"[red]Parse error: {e}[/red]")
    pause()
