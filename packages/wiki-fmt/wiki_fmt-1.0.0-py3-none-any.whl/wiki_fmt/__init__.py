#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki-fmt: Confluence 文档自动排版工具

一个支持 LLM 智能排版优化的 Confluence 文档处理工具
"""

__version__ = "1.0.0"
__author__ = "water"
__email__ = "yywater68@gmail.com"
__description__ = "一个 Confluence 文档自动排版工具，支持 LLM 智能排版优化"

from .formatter import ConfluenceFormatter

__all__ = ["ConfluenceFormatter"] 