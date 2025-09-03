from __future__ import annotations
import os, time, json
from typing import Any, Dict, Optional
import requests  # used for job polling & raw v2 endpoints
from firecrawl import Firecrawl
from .types import ScrapeOptions, CrawlOptions, SearchOptions, ExtractOptions

FIRECRAWL_BASE = "https://api.firecrawl.dev/v2"

class FirecrawlClient:
    """
    Isolated Firecrawl wrapper.
    - Uses official SDK for simple calls
    - Uses REST + polling for async endpoints (/crawl, /extract)
    """

    def __init__(self, api_key: Optional[str] = None, default_timeout_ms: int = 30000):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise RuntimeError("FIRECRAWL_API_KEY not set")
        self.sdk = Firecrawl(api_key=self.api_key)
        self.default_timeout_ms = default_timeout_ms
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ---------- SCRAPE ----------
    def scrape(self, url: str, opts: Optional[ScrapeOptions] = None) -> Dict[str, Any]:
        """
        Synchronous single-page scrape.
        Returns Firecrawl 'data' (markdown/html/links/metadata/etc.).
        """
        opts = opts or ScrapeOptions()
        payload = {
            "url": url,
            "formats": opts.formats,
            "onlyMainContent": opts.only_main_content,
            "includeTags": opts.include_tags,
            "excludeTags": opts.exclude_tags,
            "maxAge": opts.max_age_ms,
            "waitFor": opts.wait_for_ms,
            "mobile": opts.mobile,
            "timeout": opts.timeout_ms,
            "parsers": opts.parsers,
            "removeBase64Images": opts.remove_base64_images,
            "blockAds": opts.block_ads,
            "proxy": opts.proxy,
            "storeInCache": opts.store_in_cache,
        }
        if opts.location:
            payload["location"] = opts.location
        if opts.actions:
            payload["actions"] = opts.actions

        # SDK supports scrape via search(... scrape_options=...) or direct; use raw POST to stay v2-explicit
        r = requests.post(f"{FIRECRAWL_BASE}/scrape", headers=self._headers, data=json.dumps(payload), timeout=(opts.timeout_ms/1000)+5)
        r.raise_for_status()
        res = r.json()
        if not res.get("success"):
            raise RuntimeError(f"Scrape failed: {res}")
        return res["data"]

    # ---------- SEARCH ----------
    def search(self, options: SearchOptions) -> Dict[str, Any]:
        """
        Search web/news/images (optionally scrape each result with formats).
        Returns JSON from SDK.
        """
        kwargs: Dict[str, Any] = {
            "query": options.query,
            "limit": options.limit,
        }
        if options.sources:
            kwargs["sources"] = options.sources
        if options.categories:
            kwargs["categories"] = options.categories
        if options.tbs:
            kwargs["tbs"] = options.tbs
        if options.location:
            kwargs["location"] = options.location
        if options.timeout_ms:
            kwargs["timeout"] = options.timeout_ms
        if options.scrape_options:
            kwargs["scrape_options"] = _scrape_opts_to_dict(options.scrape_options)
        # SDK returns .search(...) as a normal dict
        return self.sdk.search(**kwargs)

    # ---------- CRAWL (async job) ----------
    def crawl(self, options: CrawlOptions, poll: bool = True, poll_interval_s: float = 2.0, timeout_s: int = 1800) -> Dict[str, Any]:
        """
        Start a crawl job; if poll=True, wait for completion and return final payload with all pages.
        """
        payload = {
            "url": options.url,
            "prompt": options.prompt,
            "includePaths": options.include_paths,
            "excludePaths": options.exclude_paths,
            "maxDiscoveryDepth": options.max_discovery_depth,
            "sitemap": options.sitemap,
            "ignoreQueryParameters": options.ignore_query_parameters,
            "limit": options.limit,
            "crawlEntireDomain": options.crawl_entire_domain,
            "allowExternalLinks": options.allow_external_links,
            "allowSubdomains": options.allow_subdomains,
            "delay": options.delay_ms,
            "maxConcurrency": options.max_concurrency,
            "zeroDataRetention": options.zero_data_retention,
        }
        if options.scrape_options:
            payload["scrapeOptions"] = _scrape_opts_to_dict(options.scrape_options)
        if options.webhook:
            payload["webhook"] = options.webhook

        r = requests.post(f"{FIRECRAWL_BASE}/crawl", headers=self._headers, data=json.dumps(payload), timeout=(self.default_timeout_ms/1000)+5)
        r.raise_for_status()
        start = r.json()
        if not start.get("success"):
            raise RuntimeError(f"Crawl start failed: {start}")

        job_id = start["id"]
        if not poll:
            return start

        # Poll /v2/crawl/status?id=...
        deadline = time.time() + timeout_s
        last = None
        while time.time() < deadline:
            s = requests.get(f"{FIRECRAWL_BASE}/crawl/status?id={job_id}", headers=self._headers, timeout=30)
            s.raise_for_status()
            status = s.json()
            last = status
            # Firecrawl returns { success, status: "completed"/"running"/..., data?: ... }
            if status.get("status") == "completed":
                return status
            if status.get("status") in {"failed", "error", "cancelled"}:
                raise RuntimeError(f"Crawl failed: {status}")
            time.sleep(poll_interval_s)
        raise TimeoutError(f"Crawl timed out for job {job_id}, last={last}")

    # ---------- EXTRACT (async job) ----------
    def extract(self, options: ExtractOptions, poll: bool = True, poll_interval_s: float = 2.0, timeout_s: int = 900) -> Dict[str, Any]:
        """
        Extract structured data using a prompt or schema over a list of URLs or a wildcard domain.
        """
        body: Dict[str, Any] = {"inputs": options.inputs}
        if options.prompt:
            body["prompt"] = options.prompt
        if options.schema:
            body["schema"] = options.schema
        if options.scrape_options:
            body["scrapeOptions"] = _scrape_opts_to_dict(options.scrape_options)

        r = requests.post(f"{FIRECRAWL_BASE}/extract", headers=self._headers, data=json.dumps(body), timeout=(self.default_timeout_ms/1000)+5)
        r.raise_for_status()
        start = r.json()
        if not start.get("success"):
            raise RuntimeError(f"Extract start failed: {start}")

        job_id = start["id"]
        if not poll:
            return start

        deadline = time.time() + timeout_s
        last = None
        while time.time() < deadline:
            s = requests.get(f"{FIRECRAWL_BASE}/extract/status?id={job_id}", headers=self._headers, timeout=30)
            s.raise_for_status()
            status = s.json()
            last = status
            if status.get("status") == "completed":
                return status
            if status.get("status") in {"failed", "error", "cancelled"}:
                raise RuntimeError(f"Extract failed: {status}")
            time.sleep(poll_interval_s)
        raise TimeoutError(f"Extract timed out for job {job_id}, last={last}")

def _scrape_opts_to_dict(o: ScrapeOptions) -> Dict[str, Any]:
    d = {
        "formats": o.formats,
        "onlyMainContent": o.only_main_content,
        "includeTags": o.include_tags,
        "excludeTags": o.exclude_tags,
        "maxAge": o.max_age_ms,
        "waitFor": o.wait_for_ms,
        "mobile": o.mobile,
        "timeout": o.timeout_ms,
        "parsers": o.parsers,
        "removeBase64Images": o.remove_base64_images,
        "blockAds": o.block_ads,
        "proxy": o.proxy,
        "storeInCache": o.store_in_cache,
    }
    if o.location:
        d["location"] = o.location
    if o.actions:
        d["actions"] = o.actions
    return d