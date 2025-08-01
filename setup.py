#!/usr/bin/env python3
"""
Setup script for entra-scopes-finder CLI tool.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="entra-scopes-finder",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool for finding Azure first party clients with pre-consented scopes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kidtronnix/azure-clients",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.20.0",
    ],
    entry_points={
        "console_scripts": [
            "entra-scopes-finder=entra_scopes_finder.cli:main",
            "esf=entra_scopes_finder.cli:main",  # Short alias
        ],
    },
    keywords="azure entra security scopes oauth red-team",
    project_urls={
        "Bug Reports": "https://github.com/kidtronnix/azure-clients/issues",
        "Source": "https://github.com/kidtronnix/azure-clients",
    },
)
