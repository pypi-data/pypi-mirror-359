from setuptools import setup, find_packages
from pathlib import Path

# Get the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="repo-notifier",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "repo-notifier = notifier.notifier:main",
        ],
    },
    author="Priyanshu Raj",
    author_email="your_email@example.com",  # Optional: Add a real email
    description="A CLI tool that emails a friend when you create a new GitHub repo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Priyanshu-1477/repo-notifier",  # Make sure this is correct
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
