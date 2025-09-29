# settings.py

BOT_NAME = "voice_of_morocco"

SPIDER_MODULES = ["voice_of_morocco.spiders"]
NEWSPIDER_MODULE = "voice_of_morocco.spiders"

# Respect robots.txt
ROBOTSTXT_OBEY = True

# Networking and politeness
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0 Safari/537.36"
)
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "ar,en;q=0.9",
}

# AutoThrottle to be nice with the target site
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 5
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Concurrency and delay
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.5

# Pipelines (optional)
ITEM_PIPELINES = {
    "voice_of_morocco.pipelines.VoiceOfMoroccoPipeline": 300,
}

# Export encoding (important for Arabic text)
FEED_EXPORT_ENCODING = "utf-8"
