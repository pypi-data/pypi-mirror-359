#!/usr/bin/env python3
"""Setup script for slack_error_notifier."""

from pathlib import Path
from setuptools import setup

# Project root (where setup.py, module, and README.md live)
ROOT = Path(__file__).parent
readme_path = ROOT / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else "Slack error notification helper."

setup(
    name="slack_error_notifier",
    version="1.0.4",
    description="Library to send notifications for uncaught exceptions to Slack from Python jobs (cron, ETL, CI pipelines, and services)",
    url="https://github.com/Burnwood-ccdocs/Slack-error-notifier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sarthak Sharma",
    author_email="sarthak0610@gmail.com",
    py_modules=["slack_error_notifier"],
    install_requires=["slack_sdk>=3.19.0"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    project_urls={
        "Homepage": "https://github.com/Burnwood-ccdocs/Slack-error-notifier",
        "Source": "https://github.com/Burnwood-ccdocs/Slack-error-notifier",
    },
    include_package_data=True,
    package_data={
        "": ["README.md"],
    },
)
