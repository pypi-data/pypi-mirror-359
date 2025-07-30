from setuptools import setup, find_packages

setup(
    name="repo-notifier",
    version="0.1.1",
    description="A CLI tool to notify via email when a new GitHub repo is created.",
    author="Priyanshu Raj",
    author_email="your-email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "repo-notifier = notifier.notifier:main",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.1",
)
