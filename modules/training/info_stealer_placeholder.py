"""Disabled Info Stealer training structure.

This module intentionally contains no credential, cookie, token, session,
browser-secret, key, or private-data collection implementation.
"""

from rich.panel import Panel

from core.ui import console


SAFETY_LOCK = True


class InfoStealerSafetyError(RuntimeError):
    """Raised whenever execution reaches the disabled collection boundary."""


def safety_guard():
    if SAFETY_LOCK:
        raise InfoStealerSafetyError(
            "Info Stealer is disabled by the VOID RuntimeError safety lock."
        )


def collect_browser_secrets():
    """Disabled boundary for browser-secret collection."""
    safety_guard()


def collect_session_data():
    """Disabled boundary for cookies, tokens, and session material."""
    safety_guard()


def collect_private_credentials():
    """Disabled boundary for saved credentials and private keys."""
    safety_guard()


def collect_demo_metadata():
    """Harmless structure data used only to demonstrate the module layout."""
    return {
        "module": "Info Stealer",
        "status": "disabled",
        "safety_lock": "RuntimeError",
        "collection": "not implemented",
    }


def run():
    console.print(
        Panel(
            "[bold red]Info Stealer[/bold red]\n\n"
            "[yellow]Disabled training structure.[/yellow]\n"
            "Sensitive collection boundaries are intentionally non-operational.\n"
            "Execution is blocked by a RuntimeError safety lock.",
            title="[bold white] VOID :: INFO STEALER [/bold white]",
            border_style="bright_red",
        )
    )

    metadata = collect_demo_metadata()
    for key, value in metadata.items():
        console.print(f"[red]{key}[/red]: [white]{value}[/white]")

    try:
        safety_guard()
    except InfoStealerSafetyError as exc:
        console.print(f"\n[bold red][SAFETY LOCK][/bold red] {exc}")

    input("\nPress ENTER to return...")
