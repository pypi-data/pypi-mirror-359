# 📦 Repo Notifier

A simple Python CLI tool that monitors your GitHub account and sends you an email whenever a new repository is created.

---

## ✨ Features

- ✅ Detects newly created public repositories
- 📧 Sends email notifications
- 🔐 Uses environment variables for secure credentials
- 🧪 Easy to test and extend
- 💻 Usable from terminal via `repo-notifier` command

---

## 📥 Installation

```bash
pip install repo-notifier
```

---

## ⚙️ Setup

1. **Create a `.env` file** in your working directory with the following variables:

```
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password
RECEIVER_EMAIL=recipient_email@gmail.com
```

> ⚠️ Make sure to [generate a GitHub Personal Access Token (classic)](https://github.com/settings/tokens) with `repo` and `read:user` scopes.  
> ⚠️ For Gmail, use an [App Password](https://support.google.com/mail/answer/185833?hl=en) (not your actual password).

---

## 🚀 Usage

Run the tool using:

```bash
repo-notifier
```

If a new repo is detected, you’ll receive an email with a link to the new repository.

---

## 📂 File Structure

```
repo-notifier/
├── notifier/
│   ├── __init__.py
│   └── notifier.py
├── .env                  # Your secrets (not committed)
├── README.md
├── setup.py
├── pyproject.toml
└── MANIFEST.in
```

---

## 🛠 Example Email

```
Subject: New GitHub Repo: my-new-project

Hey! 👋

A new GitHub repository was just created:
🔗 https://github.com/your_username/my-new-project

Check it out!

– Your GitHub Notifier Bot
```

---

## 📃 License

MIT © 2025 Priyanshu Raj
