MADE_BY = "Made by unbeau"

from core.ui import console, module_header, pause

ALLOWED_COMMANDS = {
    "whoami": "training-user",
    "hostname": "void-lab",
    "pwd": "/safe/mock/environment",
    "help": "whoami, hostname, pwd, help, exit"
}

def run():
    module_header("MOCK SHELL", "Training / Local Only")
    console.print("[yellow]No sockets and no operating-system command execution.[/yellow]")

    while True:
        command = input("mock-shell> ").strip().lower()
        if command in {"exit", "quit"}:
            break
        console.print(ALLOWED_COMMANDS.get(command, "Blocked command"))

    pause()
