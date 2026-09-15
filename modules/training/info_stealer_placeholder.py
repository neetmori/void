# modules/training/info_stealer_placeholder.py

from dataclasses import dataclass
from typing import Callable


@dataclass
class TrainingModule:
    name: str
    description: str
    function: Callable


MODULES: list[TrainingModule] = []


def register_module(name: str, description: str):
    def decorator(function: Callable):
        MODULES.append(
            TrainingModule(
                name=name,
                description=description,
                function=function,
            )
        )
        return function

    return decorator


@register_module(
    "System Information",
    "Displays basic non-sensitive system information.",
)
def system_information():
    import platform

    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }


@register_module(
    "Environment Test",
    "Checks whether the training environment is working.",
)
def environment_test():
    return {
        "status": "ok",
        "message": "Training environment is operational.",
    }


def execute_module(module: TrainingModule):
    try:
        result = module.function()

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


def run(url=""):
    try:
        from core.ui import console, module_header, pause
    except ImportError:
        console = None
        module_header = None
        pause = None

    if module_header:
        module_header(
            "Info Stealer",
            "Training Environment",
        )

    results = []

    for index, module in enumerate(MODULES, start=1):
        if console:
            console.print(
                f"[cyan][{index}/{len(MODULES)}][/cyan] "
                f"[bold]{module.name}[/bold]"
            )
            console.print(f"[dim]{module.description}[/dim]")

        result = execute_module(module)
        results.append(result)

        if console:
            if result["success"]:
                console.print("[green]Completed[/green]")

                data = result.get("result")

                if isinstance(data, dict):
                    for key, value in data.items():
                        console.print(f"  [dim]{key}:[/dim] {value}")
            else:
                console.print(
                    f"[red]Failed:[/red] {result.get('error')}"
                )

            console.print()

    if console:
        console.print(
            f"[bold green]{len(results)} training modules processed.[/bold green]"
        )

    if pause:
        pause()

    return results
