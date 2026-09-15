from dataclasses import dataclass
from typing import Callable


@dataclass
class RegisteredModule:
    code: str
    name: str
    description: str
    handler: Callable[[str], object]


MODULES: dict[str, RegisteredModule] = {}


def register_module(code: str, name: str, description: str):
    def decorator(function: Callable[[str], object]):
        MODULES[code] = RegisteredModule(
            code=code,
            name=name,
            description=description,
            handler=function,
        )
        return function

    return decorator


@register_module(
    "01",
    "Example Module",
    "Template showing where to add module logic.",
)
def example_module(url: str):
    result = f"Received target: {url}"

    return {
        "target": url,
        "result": result,
    }


def execute_module(module: RegisteredModule, url: str):
    try:
        result = module.handler(url)
        return {
            "module": module.name,
            "success": True,
            "result": result,
        }
    except Exception as error:
        return {
            "module": module.name,
            "success": False,
            "error": str(error),
        }


def render_result(console, result: dict):
    if not result["success"]:
        console.print(f"[red]Failed:[/red] {result.get('error')}")
        return

    console.print("[green]Completed[/green]")
    data = result.get("result")

    if isinstance(data, dict):
        for key, value in data.items():
            console.print(f"  [dim]{key}:[/dim] {value}")
    elif data is not None:
        console.print(str(data))


def run(url=""):
    from core.ui import console, module_header, pause

    while True:
        module_header("Info Stealer", "Module Registry")

        for code in sorted(MODULES):
            module = MODULES[code]
            console.print(f"[cyan][{module.code}][/cyan] [bold]{module.name}[/bold]")
            console.print(f"     [dim]{module.description}[/dim]")

        console.print("[cyan][00][/cyan] Back")
        console.print()

        choice = console.input("[bold cyan]Select:[/bold cyan] ").strip()

        if choice == "00":
            return

        module = MODULES.get(choice)

        if module is None:
            console.print("[red]Invalid option.[/red]")
            pause()
            continue

        target_url = url.strip() if url else ""

        if not target_url:
            target_url = console.input("[bold cyan]URL:[/bold cyan] ").strip()

        if not target_url:
            console.print("[red]URL is required.[/red]")
            pause()
            continue

        console.print()
        console.print(f"[bold]{module.name}[/bold]")
        console.print(f"[dim]Target: {target_url}[/dim]")

        result = execute_module(module, target_url)
        render_result(console, result)
        pause()
