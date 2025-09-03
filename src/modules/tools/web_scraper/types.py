
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal

MarkdownFormat = Literal["markdown"]
HtmlFormat = Literal["html"]
LinksFormat = Literal["links"]
ScreenshotFormat = Literal["screenshot"]

@dataclass
class ScrapeOptions:
    formats: List[Any] = field(default_factory=lambda: ["markdown"])  # can mix strings & dicts per v2
    only_main_content: bool = True
    include_tags: List[str] = field(default_factory=list)
    exclude_tags: List[str] = field(default_factory=list)
    max_age_ms: Optional[int] = 2 * 24 * 60 * 60 * 1000  # v2 defaults ~2d cache
    wait_for_ms: int = 0
    mobile: bool = False
    timeout_ms: int = 30000
    parsers: List[str] = field(default_factory=list)  # e.g., ["pdf"]
    remove_base64_images: bool = True
    block_ads: bool = True
    proxy: Literal["auto", "basic", "stealth"] = "auto"
    store_in_cache: bool = True
    location: Optional[Dict[str, Any]] = None  # {"country":"US","languages":["en-US"]}
    actions: Optional[List[Dict[str, Any]]] = None  # playwright-like actions

@dataclass
class CrawlOptions:
    url: str
    prompt: Optional[str] = None
    include_paths: List[str] = field(default_factory=list)
    exclude_paths: List[str] = field(default_factory=list)
    max_discovery_depth: Optional[int] = None
    sitemap: Literal["include", "skip"] = "include"
    ignore_query_parameters: bool = False
    limit: Optional[int] = None
    crawl_entire_domain: bool = False
    allow_external_links: bool = False
    allow_subdomains: bool = False
    delay_ms: Optional[int] = None
    max_concurrency: Optional[int] = None
    scrape_options: Optional[ScrapeOptions] = None
    webhook: Optional[Dict[str, Any]] = None
    zero_data_retention: bool = False

@dataclass
class SearchOptions:
    query: str
    limit: int = 5
    sources: Optional[List[Literal["web","news","images"]]] = None
    categories: Optional[List[Literal["github","research"]]] = None
    tbs: Optional[str] = None          # time-based search, e.g. "qdr:d"
    location: Optional[str] = None     # e.g., "Germany"
    timeout_ms: Optional[int] = None
    scrape_options: Optional[ScrapeOptions] = None

@dataclass
class ExtractOptions:
    # Either pass explicit URLs or a wildcard like "example.com/*"
    inputs: List[str]
    # Choose one:
    prompt: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    scrape_options: Optional[ScrapeOptions] = None