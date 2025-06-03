#!/usr/bin/env python3
"""Setup script for Transcriber."""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-music-transcription",
    version="0.1.0",
    author="Transcriber Team",
    author_email="contact@example.com",
    description="Tool for converting piano scores to brass arrangements",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/flynndcs/ai-music-transcription",
    project_urls={
        "Bug Tracker": "https://github.com/flynndcs/ai-music-transcription/issues",
        "Documentation": "https://github.com/flynndcs/ai-music-transcription/docs",
        "Source Code": "https://github.com/flynndcs/ai-music-transcription",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "transcriber=transcriber.brass_arranger:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)