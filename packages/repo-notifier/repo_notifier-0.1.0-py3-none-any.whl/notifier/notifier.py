# notifier/notifier.py

import requests
import json
import os
import smtplib
from email.message import EmailMessage
from rich import print
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get secrets from environment variables
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
    REPO_FILE = "repos.json"

    def send_email(new_repo_name):
        subject = f"New GitHub Repo: {new_repo_name}"
        body = f"""Hey! 👋

A new GitHub repository was just created:
🔗 https://github.com/{GITHUB_USERNAME}/{new_repo_name}

Check it out!

– Your GitHub Notifier Bot
"""
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(SENDER_EMAIL, APP_PASSWORD)
                smtp.send_message(msg)
            print(f"[green]📧 Email sent for: {new_repo_name}[/green]")
        except Exception as e:
            print(f"[red]❌ Failed to send email: {e}[/red]")

    # ==== FETCH CURRENT REPOS ====
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?sort=created&direction=desc"
    response = requests.get(url, auth=(GITHUB_USERNAME, GITHUB_TOKEN))

    if response.status_code != 200:
        print(f"[red]❌ Failed to fetch repos: {response.status_code}[/red]")
        return

    repos_data = response.json()
    current_repo_names = [repo["name"] for repo in repos_data]

    # ==== LOAD OLD REPOS ====
    if os.path.exists(REPO_FILE):
        with open(REPO_FILE, "r") as f:
            old_repo_names = json.load(f)
    else:
        old_repo_names = []

    # ==== DETECT NEW REPOS ====
    new_repos = [name for name in current_repo_names if name not in old_repo_names]

    if new_repos:
        print(f"[green]✅ New repository found:[/green]")
        for name in new_repos:
            print(f"   ➕ {name}")
            send_email(name)
    else:
        print("[yellow]No new repositories found.[/yellow]")

    # ✅ Always update the stored repo list
    with open(REPO_FILE, "w") as f:
        json.dump(current_repo_names, f, indent=2)
