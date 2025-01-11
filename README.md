# Web Crawler

A Python-based web crawler that uses Selenium and BeautifulSoup for crawling and scraping product URLs from e-commerce websites. This crawler supports multi-threading, user-agent rotation, and infinite scrolling for efficient and scalable crawling.

## Features

- **Headless Chrome WebDriver**: Uses Selenium WebDriver with Chrome in headless mode for web scraping.
- **Product URL Detection**: Identifies product pages based on URL patterns like `/dp/`, `/product/`, `/buy`, etc.
- **Listing Page Detection**: Identifies listing pages based on keywords like `tshirts`, `pants`, `jeans`, etc.
- **Recursive Crawling**: Crawls pages recursively up to a specified depth.
- **Multi-threading**: Uses Python's `ThreadPoolExecutor` to crawl multiple links concurrently for faster processing.
- **Exclusion Filters**: Excludes certain URLs (e.g., login, signup, privacy) from being crawled.
- **User-Agent Rotation**: Rotates user-agent strings to avoid detection as a bot.
- **Infinite Scrolling**: Supports infinite scrolling on pages to load all content before extracting links.
- **Result Callback**: Optionally sends crawled URLs to a callback function for further processing.

## Getting Started

### Prerequisites

Before getting started, you need to have the following installed:

- Chrome (for running the headless browser)  
- [Google Chrome Driver](https://sites.google.com/a/chromium.org/chromedriver/)  
- [Selenium](https://www.selenium.dev/documentation/en/webdriver/)  
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)  

