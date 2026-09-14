from rich.panel import Panel
from core.ui import console


def run():
    console.print(
        Panel(
            "[bold red]Info Stealer[/bold red]\n\n"
            "[yellow]Placeholder only.[/yellow]\n"
            "This menu entry does not include or execute credential-collection code.",
            title="[bold white] VOID :: INFO STEALER [/bold white]",
            border_style="bright_red",
        )
    )
    input("\nPress ENTER to return...")
