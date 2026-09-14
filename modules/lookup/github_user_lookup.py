import requests
from rich.table import Table

from core.logger import save_log
from core.ui import console, module_header, pause


def fetch_json(url):
    response = requests.get(url, timeout=15, headers={"Accept": "application/vnd.github+json", "User-Agent": "VOID/1.0"})
    if response.status_code == 404:
        raise ValueError("GitHub user not found")
    response.raise_for_status()
    return response.json(), response.headers


def run():
    module_header("GitHub User Lookup", "OSINT")
    username = console.input("[bold white]GitHub username:[/bold white] ").strip()
    if not username:
        console.print("[red]Username is required.[/red]")
        pause()
        return

    try:
        profile, headers = fetch_json(f"https://api.github.com/users/{username}")
        repos, _ = fetch_json(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated")
        orgs, _ = fetch_json(f"https://api.github.com/users/{username}/orgs?per_page=100")
        events, _ = fetch_json(f"https://api.github.com/users/{username}/events/public?per_page=100")
    except (requests.RequestException, ValueError) as exc:
        console.print(f"[red]GitHub lookup failed: {exc}[/red]")
        pause()
        return

    table = Table(title=f"GitHub Profile · {profile.get('login')}", show_header=False, border_style="red")
    table.add_column("Field", style="bold red")
    table.add_column("Value", style="white")
    fields = [
        ("ID", profile.get("id")),
        ("Node ID", profile.get("node_id")),
        ("Name", profile.get("name")),
        ("Type", profile.get("type")),
        ("Company", profile.get("company")),
        ("Blog", profile.get("blog")),
        ("Location", profile.get("location")),
        ("Public Email", profile.get("email")),
        ("Hireable", profile.get("hireable")),
        ("Bio", profile.get("bio")),
        ("Twitter", profile.get("twitter_username")),
        ("Followers", profile.get("followers")),
        ("Following", profile.get("following")),
        ("Public Repositories", profile.get("public_repos")),
        ("Public Gists", profile.get("public_gists")),
        ("Created", profile.get("created_at")),
        ("Updated", profile.get("updated_at")),
        ("Profile URL", profile.get("html_url")),
        ("Avatar URL", profile.get("avatar_url")),
    ]
    for label, value in fields:
        if value not in (None, ""):
            table.add_row(label, str(value))
    console.print(table)

    repo_table = Table(title="Public Repositories", border_style="red")
    repo_table.add_column("Repository", style="bold white")
    repo_table.add_column("Language")
    repo_table.add_column("Stars", justify="right")
    repo_table.add_column("Forks", justify="right")
    repo_table.add_column("Updated")
    for repo in repos[:50]:
        repo_table.add_row(
            str(repo.get("name") or ""),
            str(repo.get("language") or ""),
            str(repo.get("stargazers_count") or 0),
            str(repo.get("forks_count") or 0),
            str(repo.get("updated_at") or ""),
        )
    if repo_table.row_count:
        console.print(repo_table)

    languages = {}
    total_stars = 0
    total_forks = 0
    for repo in repos:
        language = repo.get("language")
        if language:
            languages[language] = languages.get(language, 0) + 1
        total_stars += repo.get("stargazers_count") or 0
        total_forks += repo.get("forks_count") or 0

    event_types = {}
    for event in events:
        event_type = event.get("type") or "Unknown"
        event_types[event_type] = event_types.get(event_type, 0) + 1

    summary = Table(title="Public Activity Summary", show_header=False, border_style="red")
    summary.add_column("Field", style="bold red")
    summary.add_column("Value", style="white")
    summary.add_row("Organizations", ", ".join(org.get("login", "") for org in orgs) or "None public")
    summary.add_row("Languages", ", ".join(f"{key}:{value}" for key, value in sorted(languages.items(), key=lambda item: item[1], reverse=True)) or "Unknown")
    summary.add_row("Repository Stars", str(total_stars))
    summary.add_row("Repository Forks", str(total_forks))
    summary.add_row("Recent Public Events", str(len(events)))
    summary.add_row("Event Types", ", ".join(f"{key}:{value}" for key, value in sorted(event_types.items())) or "None")
    summary.add_row("API Rate Limit Remaining", headers.get("X-RateLimit-Remaining", "Unknown"))
    console.print(summary)

    path = save_log("github_user_lookup", username, {"profile": profile, "repositories": repos, "organizations": orgs, "public_events": events})
    console.print(f"[dim]Log saved to {path}[/dim]")
    pause()
