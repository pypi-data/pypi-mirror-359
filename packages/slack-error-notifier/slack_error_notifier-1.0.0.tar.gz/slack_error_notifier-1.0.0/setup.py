#!/usr/bin/env python3
"""Setup script for slack_error_notifier."""

from setuptools import setup

setup(
    name="slack_error_notifier",
    version="1.0.0",
    description="Simple library for sending error notifications to Slack",
    author="Your Name",
    author_email="your.email@example.com",
    py_modules=["slack_error_notifier"],
    install_requires=["slack_sdk>=3.19.0"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 