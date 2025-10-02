import scrapy
from datetime import datetime
import logging
import re

class VoiceSpider(scrapy.Spider):
    name = "voice"
    allowed_domains = ["thevoice.ma"]
    
    # Start with page 1 (main category page)
    start_urls = ["https://thevoice.ma/category/societe/"]
    
    # Configure settings
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/articles.json',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    def __init__(self, *args, **kwargs):
        super(VoiceSpider, self).__init__(*args, **kwargs)
        # Target date range: from September 21st until today
        self.start_date = datetime(2025, 9, 21).date()
        self.end_date = datetime.now().date()
        self.stop_date = datetime(2025, 9, 20).date()  # Stop when we reach September 20th
        
        # Arabic month mappings
        self.arabic_months = {
            'يناير': 1, 'فبراير': 2, 'مارس': 3, 'أبريل': 4, 'ماي': 5, 'مايو': 5,
            'يونيو': 6, 'يوليو': 7, 'غشت': 8, 'أغسطس': 8, 'شتنبر': 9, 'سبتمبر': 9,
            'أكتوبر': 10, 'نونبر': 11, 'نوفمبر': 11, 'دجنبر': 12, 'ديسمبر': 12
        }
        
        self.articles_found = 0
        self.should_stop = False

    def parse_arabic_date(self, date_text):
        """Parse Arabic date format like 'الأحد 28 سبتمبر 2025 - 18:58'"""
        if not date_text:
            return None
            
        try:
            # Remove day name and time part
            date_part = date_text.split(' - ')[0].strip()
            
            # Extract day, month, year using regex
            match = re.search(r'(\d{1,2})\s+([^\d\s]+)\s+(\d{4})', date_part)
            if match:
                day = int(match.group(1))
                month_arabic = match.group(2)
                year = int(match.group(3))
                
                # Convert Arabic month to number
                month = self.arabic_months.get(month_arabic)
                if month:
                    return datetime(year, month, day).date()
                    
        except Exception as e:
            self.logger.warning(f"Could not parse date '{date_text}': {e}")
            
        return None

    def is_within_date_range(self, date_text):
        """Check if date is within our target range (Sept 21 to today)"""
        parsed_date = self.parse_arabic_date(date_text)
        if parsed_date:
            # Check if we reached September 20th (stop condition)
            if parsed_date <= self.stop_date:
                self.should_stop = True
                self.logger.info(f"🛑 Reached stop date: {parsed_date}. Stopping crawl.")
                return False
            
            # Check if date is within our target range (Sept 21 to today)
            return self.start_date <= parsed_date <= self.end_date
        return False

    def extract_arabic_author(self, response):
        """
        Extract Arabic author name from the author box structure
        Based on the HTML structure you provided
        """
        # Method 1: Try to extract from author-name span (direct text)
        author_name = response.css('span.author-name a::text').get()
        if author_name and author_name.strip():
            return author_name.strip()
        
        # Method 2: Try to extract from the author box content
        author_name = response.css('.author-box .author-name::text').get()
        if author_name and author_name.strip():
            return author_name.strip()
        
        # Method 3: Try to extract from the author data section
        author_name = response.css('.author-data .author-name::text').get()
        if author_name and author_name.strip():
            return author_name.strip()
        
        # Method 4: Try to extract from any author-related elements with more specific selectors
        author_selectors = [
            '.author-box-content .author-name a::text',
            '.author-box .author-data .author-name a::text',
            'span.author-name::text',
            '.post-author a::text',
            'a[rel="author"]::text',
            'span.byline a::text',
            'div.author a::text'
        ]
        
        for selector in author_selectors:
            author_name = response.css(selector).get()
            if author_name and author_name.strip():
                return author_name.strip()
        
        # Method 5: If all else fails, try to extract from meta tags
        author_name = response.css('meta[name="author"]::attr(content)').get()
        if author_name and author_name.strip():
            return author_name.strip()
            
        self.logger.warning(f"Could not extract author name from: {response.url}")
        return ""

    def parse(self, response):
        """
        Parse the category page: extract article links and pagination.
        """
        # Check if we should stop crawling
        if self.should_stop:
            self.logger.info("🛑 Stop condition met. Ending crawl.")
            return
            
        self.logger.info(f'Parsing category page: {response.url}')
        
        # Try multiple selectors to find article links
        article_selectors = [
            'h2.entry-title a::attr(href)',
            'h2.title a::attr(href)',
            'h2 a::attr(href)',
            'a.entry-title-link::attr(href)',
            'article a:has(img)::attr(href)',
            'div.post-item a::attr(href)'
        ]
        
        article_links = []
        for selector in article_selectors:
            links = response.css(selector).getall()
            if links:
                article_links = links
                self.logger.info(f'Found {len(links)} articles using selector: {selector}')
                break
        
        if not article_links:
            self.logger.warning('No article links found on page.')
            
        # Follow article links
        for link in article_links:
            if '/category/' not in link and not self.should_stop:  # Skip category links
                yield response.follow(link, callback=self.parse_article)
                
        # Handle pagination only if we haven't reached stop condition
        if not self.should_stop:
            next_selectors = [
                'a.next::attr(href)',
                'a.next.page-numbers::attr(href)',
                'li.pagination-next a::attr(href)',
                'a[rel="next"]::attr(href)'
            ]
            
            next_page = None
            for selector in next_selectors:
                next_page = response.css(selector).get()
                if next_page:
                    self.logger.info(f'Found next page: {next_page}')
                    yield response.follow(next_page, callback=self.parse)
                    break

    def parse_article(self, response):
        """
        Parse an article page and extract required info.
        """
        # Check if we should stop processing
        if self.should_stop:
            return
            
        self.logger.info(f'Parsing article: {response.url}')
        
        # Extract date first to check if it's in our range
        date_selectors = [
            'time.entry-date::text',
            'time.item-date::text',
            'span.date::text',
            'div.date::text',
            '.post-date::text',
            '.article-date::text',
            'meta[property="article:published_time"]::attr(content)'
        ]
        
        date_text = ''
        for selector in date_selectors:
            date_element = response.css(selector).get()
            if date_element:
                date_text = date_element.strip()
                self.logger.info(f'Found date: {date_text}')
                break
        
        # Check if article is within our date range
        if not self.is_within_date_range(date_text):
            self.logger.info(f'Skipping article - date outside range: {date_text}')
            return
        
        self.logger.info(f'✅ Article within target range: {date_text}')
        
        # Extract other fields
        def get_text(selectors):
            for selector in selectors:
                element = response.css(selector).get()
                if element:
                    return element.strip()
            return ''
            
        def get_list(selectors):
            for selector in selectors:
                elements = response.css(selector).getall()
                if elements:
                    return [e.strip() for e in elements if e.strip()]
            return []
        
        # Extract Arabic author name using the new method
        arabic_author = self.extract_arabic_author(response)
        self.logger.info(f'Extracted author: {arabic_author}')
        
        # Only include the fields we want
        item = {
            'url': response.url,
            'title': get_text([
                'h1.entry-title::text',
                'h1.title::text',
                'h1::text',
                'header h1::text',
                'h1.article-title::text'
            ]),
            'date': date_text,
            'author': arabic_author,  # Use the extracted Arabic author name
            'content': ' '.join(response.css(', '.join([
                'div.entry-content p::text',
                'div#item-content p::text',
                'div.post-content p::text',
                'article p::text',
                'div.content p::text'
            ])).getall()).strip(),
            'images': response.css(', '.join([
                'div.entry-content img::attr(src)',
                'img.wp-post-image::attr(src)',
                'figure img::attr(src)',
                'div.article-image img::attr(src)',
                'article img::attr(src)'
            ])).getall(),
            'links': response.css('div.entry-content a::attr(href)').getall(),
        }
        
        self.articles_found += 1
        self.logger.info(f'✅ Extracted article #{self.articles_found}: {item["title"][:50]}...')
        self.logger.info(f'✅ Author: {arabic_author}')
        
        yield item