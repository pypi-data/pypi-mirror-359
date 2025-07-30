# GitHub Repo Notifier 🚀

A simple CLI tool to notify your friend via email whenever a new GitHub repository is created.

This tool fetches your GitHub repos using the API and compares them to the previous list. If a new repo is found, it automatically sends an email notification.

---

## 📦 Installation (after PyPI upload)

```bash
pip install repo-notifier
```

Or install locally:

```bash
git clone https://github.com/Priyanshu-1477/github-repo-notifier.git
cd github-repo-notifier
pip install .
```

## 🚀 Usage
Once installed, run:

```bash
repo-notifier
```

## Make sure you have a .env file in the current directory with the following keys:

```env
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_app_password
RECEIVER_EMAIL=friend_email@gmail.com
```

## 🛠️ Features
Checks for new public repos on your GitHub account

Sends email to your friend when a new repo is created

Logs output with rich formatting

Can be scheduled using cron or systemd

## 🔐 Security
Secrets are handled via environment variables using a .env file and never hardcoded.

## 💡 Author


<p aligned=center>Made with ❤️ by Priyanshu Raj</p>


---

