#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for wiki-fmt
"""

from setuptools import setup, find_packages
import os

# 读取 README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "一个 Confluence 文档自动排版工具，支持 LLM 智能排版优化"

# 读取依赖
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "requests>=2.28.0",
        "python-dotenv>=0.19.0", 
        "beautifulsoup4>=4.11.0",
        "openai>=1.0.0",
        "atlassian-python-api>=3.41.0",
        "lxml>=4.9.0",
        "markdown>=3.4.0"
    ]

setup(
    name="wiki-fmt",
    version="1.0.0",
    author="water",
    author_email="yywater68@gmail.com",
    description="一个 Confluence 文档自动排版工具，支持 LLM 智能排版优化",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/water/wiki-fmt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wiki-fmt=wiki_fmt.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "wiki_fmt": ["*.md"],
    },
) 