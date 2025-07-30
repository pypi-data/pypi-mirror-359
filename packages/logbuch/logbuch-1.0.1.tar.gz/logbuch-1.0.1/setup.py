#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    # Remove sqlite3 as it's built-in
    requirements = [req for req in requirements if not req.startswith("sqlite3")]

setup(
    name="logbuch",
    version="1.0.0",
    author="Alexander Straub",
    author_email="your.email@example.com",
    description="The Ultimate AI-Powered CLI Productivity Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/logbuch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "logbuch=logbuch.cli:cli",
            "lb=logbuch.cli:cli",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "logbuch": ["*.txt", "*.md"],
    },
    keywords="productivity, cli, ai, gamification, task-management, journal, terminal",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/logbuch/issues",
        "Source": "https://github.com/yourusername/logbuch",
        "Documentation": "https://github.com/yourusername/logbuch#readme",
    },
)
