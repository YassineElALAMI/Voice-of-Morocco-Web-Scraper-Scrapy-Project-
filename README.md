# Voice of Morocco Web Scraper

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.13.3-green.svg)](https://scrapy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful web scraper for collecting news articles from The Voice Morocco (thevoice.ma), specifically designed to extract articles from the society category with support for Arabic date parsing and content extraction.

## 🚀 Features

- **Focused Crawling**: Targets specific date ranges for precise data collection
- **Arabic Date Handling**: Robust parsing of Arabic date formats
- **Content Extraction**: Comprehensive extraction of article content, including:
  - Article titles and text
  - Author information
  - Publication dates
  - Embedded images and links
  - Video content
- **Data Export**: Multiple output formats supported (JSON, CSV, JSONL)
- **Resilient**: Built-in error handling and retry mechanisms
- **Respectful Crawling**: Configurable delay and concurrency settings

## 📂 Project Structure

```
voice_of_morocco/
├── data/                           # Scraped data files
│   ├── articles.json              # JSON output of scraped articles
│   └── articles.csv               # CSV export of scraped data
├── voice_of_morocco/
│   ├── spiders/
│   │   └── news_spiders.py        # Main spider implementation
│   ├── items.py                   # Data structure definitions
│   ├── pipelines.py               # Data processing pipelines
│   └── settings.py                # Scrapy project settings
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YassineElALAMI/Voice-of-Morocco-Web-Scraper-Scrapy-Project-.git
   cd web_scraping
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Listing Available Spiders

To see all available spiders:
```bash
scrapy list
```

### Running the Spider

To start scraping articles from The Voice Morocco:

```bash
# Basic usage with JSON output
scrapy crawl voice -o data/articles.json -s FEED_EXPORT_ENCODING=utf-8

# Limit number of items (for testing)
scrapy crawl voice -O data/sample_articles.json -s CLOSESPIDER_ITEMCOUNT=10

# Filter by date range
scrapy crawl voice -O data/sept_2025_articles.json -a from_date=2025-09-01 -a to_date=2025-09-30
```

### Output Formats

The spider supports multiple output formats:
- JSON: `-o articles.json`
- JSON Lines: `-o articles.jsonl`
- CSV: `-o articles.csv`

## 📊 Data Schema

Each scraped article includes the following fields:

| Field   | Type   | Description                                      |
|---------|--------|--------------------------------------------------|
| url     | String | Canonical URL of the article                     |
| title   | String | Article title                                    |
| date    | String | Publication date in ISO format (YYYY-MM-DD)      |
| author  | String | Article author name (if available)               |
| content | String | Full text content of the article                 |
| images  | List   | URLs of images included in the article           |
| links   | List   | URLs linked within the article content           |
| videos  | List   | Video URLs or embed codes (if any)               |

## ⚙️ Configuration

Customize the scraper behavior by modifying `settings.py`:
- `DOWNLOAD_DELAY`: Delay between requests (default: 2 seconds)
- `CONCURRENT_REQUESTS`: Number of concurrent requests (default: 1)
- `AUTOTHROTTLE_ENABLED`: Enable/disable auto-throttling
- `ROBOTSTXT_OBEY`: Respect robots.txt (default: False)

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write clear, concise commit messages
- Add comments for complex logic
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact:

- **Project Maintainer**: Yassine EL ALAMI
- **Email**: yassine.elalami5@usmba.ac.ma
- **GitHub**: [YassineElALAMI](https://github.com/YassineElALAMI)

## Acknowledgments

- Built with [Scrapy](https://scrapy.org/)
- Special thanks to the Scrapy community for their amazing framework
