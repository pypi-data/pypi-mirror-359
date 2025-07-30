"""
OpenNutgraf - A Python module for article extraction and summarization

This module provides a clean API for extracting articles from URLs and generating summaries
using various LLM providers (OpenAI, Anthropic).
"""

from .client import OpenNutgrafClient
from .article_extractor import ArticleExtractor
from .llm_service import LLMService
from .models import Summary, Article, SummaryOptions

__version__ = "1.0.0"
__all__ = ["OpenNutgrafClient", "ArticleExtractor", "LLMService", "Summary", "Article", "SummaryOptions"]