from setuptools import setup, find_packages

setup(
    name="repo-notifier",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "repo-notifier = notifier.notifier:main"
        ]
    },
    author="Priyanshu Raj",
    author_email="prmahatha@gmail.com",
    description="Auto-notify a friend when a new GitHub repo is created",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Priyanshu-1477/github-repo-notifier",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
