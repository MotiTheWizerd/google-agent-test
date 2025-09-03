"""
Web Scraper Tools Module
========================

This module provides tools for web scraping, crawling, and content extraction
using the Firecrawl service. It includes:

- Web page scraping with multiple format options
- Search functionality with optional content scraping
- Site crawling with configurable depth and limits
- Structured data extraction using prompts or schemas

The tools are designed to be used by AI agents in the Agents Manager system.
"""

from .firecrawl_tools import (
    tool_scrape,
    tool_search,
    tool_crawl_site,
    tool_extract
)

__all__ = [
    "tool_scrape",
    "tool_search",
    "tool_crawl_site",
    "tool_extract"
]