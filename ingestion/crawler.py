"""
DocQuery Ingestion — Web Crawler
Crawls documentation sites and extracts structured content.
"""

import asyncio
import hashlib
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
from typing import Optional

import httpx
from bs4 import BeautifulSoup


@dataclass
class CrawledPage:
    """A single crawled documentation page."""
    url: str
    title: str
    content: str
    headings: list[dict] = field(default_factory=list)
    code_blocks: list[str] = field(default_factory=list)
    content_hash: str = ""
    doc_type: str = "conceptual"


class DocCrawler:
    """Crawls documentation sites and extracts structured content."""

    def __init__(
        self,
        base_url: str,
        max_pages: int = 100,
        max_depth: int = 5,
        delay: float = 1.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.base_domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.delay = delay
        self.visited: set[str] = set()
        self.pages: list[CrawledPage] = []

    async def crawl(self, extra_urls: list[str] | None = None) -> list[CrawledPage]:
        """Crawl the documentation site starting from base_url.

        extra_urls: Additional URLs to crawl directly (useful when JS-rendered
        navigation hides links from the static HTML crawler).
        """
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "DocQuery/1.0 (Documentation Indexer)"},
        ) as client:
            await self._crawl_page(client, self.base_url, depth=0)
            for url in (extra_urls or []):
                await self._crawl_page(client, url, depth=1)

        print(f"Crawled {len(self.pages)} pages from {self.base_url}")
        return self.pages

    async def _crawl_page(self, client: httpx.AsyncClient, url: str, depth: int):
        """Recursively crawl a single page."""
        normalized = self._normalize_url(url)

        if normalized in self.visited:
            return
        if len(self.pages) >= self.max_pages:
            return
        if depth > self.max_depth:
            return

        self.visited.add(normalized)

        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return
            if "text/html" not in resp.headers.get("content-type", ""):
                return
        except (httpx.HTTPError, httpx.TimeoutException):
            return

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script, style, nav, footer elements
        for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract content from main area
        main = soup.find("main") or soup.find("article") or soup.find(class_="content") or soup.body
        if not main:
            return

        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)

        # Extract headings with hierarchy
        headings = []
        for heading in main.find_all(["h1", "h2", "h3", "h4"]):
            level = int(heading.name[1])
            headings.append({
                "level": level,
                "text": heading.get_text(strip=True),
                "id": heading.get("id", ""),
            })

        # Extract code blocks
        code_blocks = []
        for pre in main.find_all("pre"):
            code = pre.find("code")
            if code:
                code_blocks.append(code.get_text())
            else:
                code_blocks.append(pre.get_text())

        # Get text content preserving structure
        content = self._extract_structured_text(main)
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # Detect doc type
        doc_type = self._detect_doc_type(url, title, content)

        page = CrawledPage(
            url=normalized,
            title=title,
            content=content,
            headings=headings,
            code_blocks=code_blocks,
            content_hash=content_hash,
            doc_type=doc_type,
        )
        self.pages.append(page)
        print(f"  Crawled: {title or normalized}")

        # Find and follow internal links
        await asyncio.sleep(self.delay)

        for link in main.find_all("a", href=True):
            href = link["href"]
            absolute = urljoin(url, href)
            parsed = urlparse(absolute)

            # Only follow links within the same domain
            if parsed.netloc == self.base_domain:
                clean = parsed._replace(fragment="").geturl()
                await self._crawl_page(client, clean, depth + 1)

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragment and trailing slash."""
        parsed = urlparse(url)
        normalized = parsed._replace(fragment="").geturl()
        return normalized.rstrip("/")

    def _extract_structured_text(self, element) -> str:
        """Extract text preserving headings and code blocks."""
        parts = []
        for child in element.children:
            if hasattr(child, "name"):
                if child.name in ("h1", "h2", "h3", "h4"):
                    prefix = "#" * int(child.name[1])
                    parts.append(f"\n{prefix} {child.get_text(strip=True)}\n")
                elif child.name == "pre":
                    code = child.find("code")
                    lang = ""
                    if code and code.get("class"):
                        classes = code.get("class", [])
                        for cls in classes:
                            if cls.startswith("language-"):
                                lang = cls.replace("language-", "")
                    text = (code or child).get_text()
                    parts.append(f"\n```{lang}\n{text}\n```\n")
                elif child.name == "table":
                    parts.append(f"\n{child.get_text(separator=' | ')}\n")
                elif child.name in ("ul", "ol"):
                    for li in child.find_all("li", recursive=False):
                        parts.append(f"- {li.get_text(strip=True)}")
                else:
                    text = child.get_text(strip=True)
                    if text:
                        parts.append(text)
            elif isinstance(child, str):
                text = child.strip()
                if text:
                    parts.append(text)

        return "\n".join(parts)

    def _detect_doc_type(self, url: str, title: str, content: str) -> str:
        """Heuristic doc type detection."""
        url_lower = url.lower()
        title_lower = title.lower()

        if any(kw in url_lower for kw in ["api", "reference", "endpoint"]):
            return "api-reference"
        if any(kw in url_lower for kw in ["tutorial", "getting-started", "quickstart"]):
            return "tutorial"
        if any(kw in url_lower for kw in ["guide", "admin", "setup", "config"]):
            return "admin-guide"
        if any(kw in title_lower for kw in ["api", "endpoint", "method"]):
            return "api-reference"
        if any(kw in title_lower for kw in ["tutorial", "getting started"]):
            return "tutorial"

        return "conceptual"


async def crawl_site(url: str, extra_urls: list[str] | None = None, **kwargs) -> list[CrawledPage]:
    """Convenience function to crawl a documentation site."""
    crawler = DocCrawler(url, **kwargs)
    return await crawler.crawl(extra_urls=extra_urls)
