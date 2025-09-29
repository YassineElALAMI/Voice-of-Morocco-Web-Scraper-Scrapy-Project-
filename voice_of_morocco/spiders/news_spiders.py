import scrapy
from scrapy.spiders import SitemapSpider
from urllib.parse import unquote, urlparse
from voice_of_morocco.items import JaridaItem
from datetime import datetime


class NewsSpider(SitemapSpider):
    name = "voice_news"
    allowed_domains = ["thevoice.ma", "www.thevoice.ma"]

    # Use Yoast sitemap to discover all posts
    sitemap_urls = [
        "https://thevoice.ma/sitemap_index.xml",
    ]
    # Follow main post sitemap and additional custom content sitemaps
    sitemap_follow = [
        r"post-sitemap\d*\.xml",
        r"thevoice_video-sitemap\.xml",
        r"thevoice_podcast-sitemap\.xml",
        r"thevoice_magazine-sitemap\.xml",
        r"thevoice_story-sitemap\d*\.xml",
    ]
    # Parse every URL in matched sitemaps
    sitemap_rules = [
        (r".*", "parse_article"),
    ]

    def __init__(self, from_date: str | None = None, to_date: str | None = None, *args, **kwargs):
        """
        Optional date filtering (ISO 8601, e.g. 2025-09-21). If not provided, no date filter.
        Example:
          scrapy crawl voice_news -a from_date=2025-09-21 -a to_date=2025-09-28
        """
        super().__init__(*args, **kwargs)
        self.from_date = None
        self.to_date = None
        if from_date:
            try:
                # Make date timezone-naive for comparison
                self.from_date = datetime.fromisoformat(from_date).replace(tzinfo=None)
                self.logger.info(f"Filtering from date: {self.from_date}")
            except Exception as e:
                self.logger.warning(f"Invalid from_date: {from_date}, error: {e}")
        if to_date:
            try:
                # Add end of day and make timezone-naive
                self.to_date = datetime.fromisoformat(to_date).replace(hour=23, minute=59, second=59, tzinfo=None)
                self.logger.info(f"Filtering to date: {self.to_date}")
            except Exception as e:
                self.logger.warning(f"Invalid to_date: {to_date}, error: {e}")

    def sitemap_filter(self, entries):
        """Filter entries at sitemap level to avoid downloading unwanted pages."""
        # If no date filters, yield all entries
        if not self.from_date and not self.to_date:
            for entry in entries:
                yield entry
            return
        
        filtered_count = 0
        passed_count = 0
        
        for entry in entries:
            # Skip if no lastmod (can't filter, so skip to be safe when filtering is active)
            if 'lastmod' not in entry:
                self.logger.debug(f"No lastmod for {entry.get('loc', 'unknown')}, skipping")
                filtered_count += 1
                continue
            
            try:
                # Parse sitemap date - handle different formats
                lastmod = entry['lastmod']
                # Remove timezone indicator and parse as naive datetime
                if lastmod.endswith('Z'):
                    lastmod = lastmod[:-1]  # Remove Z
                
                # Parse and remove timezone info for comparison
                if '+' in lastmod:
                    entry_date = datetime.fromisoformat(lastmod).replace(tzinfo=None)
                else:
                    entry_date = datetime.fromisoformat(lastmod)
                
                # Apply date filters
                if self.from_date and entry_date < self.from_date:
                    filtered_count += 1
                    continue
                if self.to_date and entry_date > self.to_date:
                    filtered_count += 1
                    continue
                    
                passed_count += 1
                yield entry
                
            except Exception as e:
                # If date parsing fails, skip entry when filtering is active
                self.logger.debug(f"Could not parse date {entry.get('lastmod', 'N/A')}: {e}, skipping")
                filtered_count += 1
                continue
        
        # Log filtering results
        self.logger.info(f"Sitemap filtering: {passed_count} entries passed, {filtered_count} filtered out")

    def parse_article(self, response):
        """Parse an individual article page on thevoice.ma (WordPress)."""
        
        # Get page date
        date_str = (
            response.css("meta[property='article:published_time']::attr(content)").get()
            or response.css("time[datetime]::attr(datetime)").get()
            or response.css("meta[name='article:published_time']::attr(content)").get()
        )
        
        # Double-check date filtering at page level (backup filter)
        if self.from_date or self.to_date:
            if not date_str:
                self.logger.debug(f"Skipping {response.url} - no date found")
                return
            
            try:
                # Parse date and remove timezone info
                pub_date_str = date_str
                if pub_date_str.endswith('Z'):
                    pub_date_str = pub_date_str[:-1]  # Remove Z
                
                if '+' in pub_date_str:
                    pub_dt = datetime.fromisoformat(pub_date_str).replace(tzinfo=None)
                else:
                    pub_dt = datetime.fromisoformat(pub_date_str)
                
                if self.from_date and pub_dt < self.from_date:
                    self.logger.debug(f"Skipping {response.url} - date {pub_dt.date()} before from_date {self.from_date.date()}")
                    return
                if self.to_date and pub_dt > self.to_date:
                    self.logger.debug(f"Skipping {response.url} - date {pub_dt.date()} after to_date {self.to_date.date()}")
                    return
            except Exception as e:
                self.logger.warning(f"Could not parse page date {date_str}: {e}, skipping")
                return
        
        # ... rest of your parse_article method remains the same
        item = JaridaItem()

        # Stable id from slug
        try:
            slug = urlparse(response.url).path.rstrip("/").split("/")[-1]
            item["idPost"] = unquote(slug)
        except Exception:
            item["idPost"] = response.url

        # Title (prefer on-page h1, fallback to OG title, then <title>)
        title = response.css("h1.entry-title::text").get()
        if not title:
            title = response.css("meta[property='og:title']::attr(content)").get()
        if not title:
            title = response.css("title::text").get()
        item["title"] = title

        # Published date (ISO if available)
        item["date"] = date_str

        # Article text
        paragraphs = response.css(
            "article .entry-content p::text, .entry-content p::text, article p::text"
        ).getall()
        item["text"] = " ".join([t.strip() for t in paragraphs if t and t.strip()])

        # Media
        images = response.css(
            "article img::attr(src), .entry-content img::attr(src)"
        ).getall()
        item["images"] = [response.urljoin(u) for u in images]
        videos = response.css(
            "article video::attr(src), article video source::attr(src), article iframe::attr(src), "
            ".entry-content video::attr(src), .entry-content iframe::attr(src)"
        ).getall()
        item["videos"] = [response.urljoin(u) for u in videos]

        # Links inside article
        links = response.css(
            "article .entry-content a::attr(href), article a::attr(href), .entry-content a::attr(href)"
        ).getall()
        item["links"] = [response.urljoin(u) for u in links]

        # Page URL
        item["url"] = response.url

        yield item