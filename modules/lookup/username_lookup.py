import re
import requests
from rich.table import Table
from core.logger import save_log
from core.ui import console, module_header, pause

SITES = {
    "Doxbin": "https://www.doxbin.com/{username}",
    "TikTok": "https://www.tiktok.com/@{username}",
    "Instagram": "https://www.instagram.com/{username}/",
    "YouTube": "https://www.youtube.com/@{username}",
    "Facebook": "https://www.facebook.com/{username}",
    "Roblox": "https://www.roblox.com/users/profile?username={username}",
    "Discord": "https://discord.com/users/{username}",
}

def extract_title(text):
    match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()[:160]

def search_doxbin_content(username):
    search_url = "https://doxbin.com/search"
    params = {
        "search": username,
        "search_in": "content"  # ou "title" dependendo do que quer buscar
    }
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        response = session.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            content = response.text
            # Verifique se há menções ao username no conteúdo
            if username.lower() in content.lower():
                return True
            else:
                return False
        else:
            return False
    except requests.RequestException:
        return False

def run():
    module_header("Username Lookup", "OSINT")
    username = console.input("[bold white]Username:[/bold white] ").strip().lstrip("@")
    if not username:
        console.print("[red]Username is required.[/red]")
        pause()
        return

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 VOID/1.0"})
    results = []

    for site, template in SITES.items():
        url = template.format(username=username)
        try:
            response = session.get(url, timeout=10, allow_redirects=True)
            exists = response.status_code == 200
            results.append({
                "site": site,
                "url": url,
                "final_url": response.url,
                "status": response.status_code,
                "exists": exists,
                "title": extract_title(response.text[:200_000]) if exists else None,
                "content_type": response.headers.get("Content-Type"),
            })
        except requests.RequestException as exc:
            results.append({
                "site": site,
                "url": url,
                "error": str(exc),
                "exists": False,
            })

    # Nova seção: busca no Doxbin por menções ao usuário
    doxbin_mention = search_doxbin_content(username)

    table = Table(title=f"Public Social Profiles · {username}", border_style="red")
    table.add_column("Site", style="bold red")
    table.add_column("Status")
    table.add_column("Profile")
    table.add_column("Title", style="white")
    table.add_column("URL")

    for item in results:
        table.add_row(
            item["site"],
            str(item.get("status") or "ERR"),
            "Found" if item.get("exists") else "Not confirmed",
            str(item.get("title") or item.get("error") or ""),
            item.get("final_url") or item["url"],
        )

    console.print(table)
    console.print(
        "[dim]Some platforms block automated public-profile checks or do not expose a public username URL. "
        "A result marked Found is only a public URL match and does not prove that accounts on different sites belong to the same person.[/dim]"
    )

    # Exibir resultado da busca no Doxbin
    if doxbin_mention:
        console.print("[green]Menção ao usuário no Doxbin foi encontrada.[/green]")
    else:
        console.print("[yellow]Nenhuma menção ao usuário no Doxbin foi encontrada.[/yellow]")

    found = [item for item in results if item.get("exists")]
    path = save_log(
        "username_lookup",
        username,
        {"found_count": len(found), "results": results},
    )
    console.print(f"[dim]Confirmed public profile URLs: {len(found)}[/dim]")
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
