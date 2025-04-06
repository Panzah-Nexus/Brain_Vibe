#!/usr/bin/env python3
"""
BrainVibe CLI setup
"""

from setuptools import setup, find_packages

setup(
    name="brainvibe",
    version="0.1.0",
    description="BrainVibe CLI - Track code changes and extract learning topics",
    author="BrainVibe Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "brainvibe=brainvibe.__main__:main",
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
) 