# Voice of Morocco Scrapy Project

## Overview
- **Spider**: `voice_news` in `voice_of_morocco/spiders/news_spiders.py`
- **Target**: `thevoice.ma` (WordPress)
- **Discovery**: Yoast sitemaps via `SitemapSpider`
- **Output fields**: `idPost, title, date, text, images, videos, links, url`

## Setup
1. Create and activate a virtualenv (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick checks
- List spiders:
  ```bash
  scrapy list
  ```

## Run examples
- Crawl a few items to `data/voice_news.jsonl`:
  ```bash
  scrapy crawl voice_news -O data/voice_news.jsonl -s FEED_EXPORT_ENCODING=utf-8 -s CLOSESPIDER_ITEMCOUNT=3
  ```

- Filter by date window (ISO 8601):
  ```bash
  scrapy crawl voice_news -O data/voice_news.jsonl -a from_date=2025-09-21 -a to_date=2025-09-28
  ```

## Notes
- `settings.py` enables AutoThrottle and sets a realistic User-Agent.
- `pipelines.py` cleans text and deduplicates lists while preserving order.
- Respect for `robots.txt` is enabled.
