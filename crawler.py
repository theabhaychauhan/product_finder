import re
import random
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor

class Crawler:
    def __init__(self, url, output_file="product_urls.txt"):
        """
        Initializes the Crawler with the given URL and optional output file.
        Configures Selenium WebDriver options and sets up patterns for product and listing URLs.
        """
        self.url = url
        self.visited_urls = set()  # Tracks visited URLs to avoid redundant crawling
        self.products_urls = set()  # Tracks identified product URLs
        # Patterns for identifying product pages
        self.product_url_patterns = ["/dp/", "/product/", "/buy", "/p/", "/ip/"]
        # Patterns for identifying listing pages
        self.listing_patterns = [
            "tshirts", "pants", "shirts", "jackets", "category", "catalog", "products",
            "jeans", "sweaters", "dresses", "skirts", "mobiles", "laptops", "headphones", 
            "cameras", "electronics", "furniture", "sofas", "kitchen", "beds", "decor",
            "makeup", "skincare", "health", "wellness", "watches", "bags", "sunglasses",
            "deals", "offers", "new-arrivals", "sale"
        ]
        # Patterns to exclude from crawling
        self.exclude_patterns = ["login", "signin", "signup", "contactus", "careers", "about", "terms", "privacy", "help"]
        
        # List of user agents to rotate requests
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]

        self.output_file = output_file  # File to store identified product URLs

        # Configuring Selenium WebDriver options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        self.driver = webdriver.Chrome(options=chrome_options)

    def _is_valid(self, url):
        """
        Validates if a given URL is well-formed.
        """
        url_regex = re.compile(r'^(?:http|ftp)s?://'
                               r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                               r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                               r'(?::\d+)?'
                               r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_regex.match(url))
    
    def _fetch_page(self, url):
        """
        Fetches the content of a URL using Selenium with infinite scrolling.
        Checks for product-specific features to refine patterns.
        """
        try:
            self.driver.get(url)
            time.sleep(random.uniform(1, 3))

            # Implementing infinite scrolling
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 3))
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Check for product-specific features dynamically
            if self._has_product_features():
                self._add_to_product_patterns(url)

            return self.driver.page_source
        except Exception as e:
            print(f"Skipping {url} due to {e}")
            return None

    def _has_product_features(self):
        """
        Intelligently determines if the page has product-specific features.
        Specifically checks for 'Add to cart' or 'Buy now' buttons even if 
        not hard coded before hand.
        """
        try:
            add_to_cart_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Add to cart')]")
            buy_now_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Buy now')]")
            
            total_buttons = len(add_to_cart_buttons) + len(buy_now_buttons)
            
            return total_buttons == 1
            
        except Exception as e:
            print(f"Error checking product features: {e}")
            return False

    def _add_to_product_patterns(self, url):
        """
        Increase the crawl intelligence by adding new product URL patterns based on 
        observed URLs.
        """
        for pattern in self.product_url_patterns:
            if pattern in url:
                return

        # Extracting potential patterns from the URL
        potential_pattern = url.split("/")[-2] if "/" in url else url.split("?")[0]
        if potential_pattern not in self.product_url_patterns:
            self.product_url_patterns.append(potential_pattern)
            print(f"New product URL pattern added: {potential_pattern}")

    def _extract_links(self, page_content):
        """
        Extracts and categorizes links from the page content.
        """
        soup = BeautifulSoup(page_content, "lxml", parse_only=SoupStrainer("a"))
        links = [a['href'] for a in soup.find_all("a", href=True)]

        # Exclude links with patterns in `exclude_patterns`
        links = [link for link in links if not any(exclude in link.lower() for exclude in self.exclude_patterns)]
        
        product_links = [link for link in links if self._is_product_page(link)]
        listing_links = [link for link in links if self._is_listing_page(link) and link not in product_links]
        other_links = [link for link in links if link not in product_links and link not in listing_links]
        return product_links + listing_links + other_links

    def _is_product_page(self, url):
        """
        Determines if a URL corresponds to a product page.
        """
        return any(pattern in url for pattern in self.product_url_patterns)

    def _is_listing_page(self, url):
        """
        Determines if a URL corresponds to a listing page.
        """
        url_lower = url.lower()

        if any(exclude in url_lower for exclude in self.exclude_patterns):
            return False

        for pattern in self.listing_patterns:
            plural_pattern = f"{pattern}s" if not pattern.endswith("s") else pattern
            if pattern in url_lower or plural_pattern in url_lower:
                if plural_pattern not in self.listing_patterns:
                    self.listing_patterns.append(plural_pattern)
                return True

        pagination_patterns = ["page=", "/page/", "?page="]
        for pagination in pagination_patterns:
            if pagination in url_lower:
                if pagination not in self.listing_patterns:
                    self.listing_patterns.append(pagination)
                return True

        return False

    def _sanitize_url(self, url):
        """
        Removes fragments from URLs.
        """
        return url.split('#')[0]

    def _write_to_file(self, url):
        """
        Writes a URL to the output file.
        """
        with open(self.output_file, "a") as f:
            f.write(url + "\n")

    def _print_logs(self, url):
        """
        Logs crawled URLs to the console. For my development and ease of spotting the results
        """
        print(f"\033[91m{url}\033[0m")

    def _recursive_crawl(self, current_url, current_depth, max_depth):
        """
        Recursively crawls pages starting from the given URL up to the maximum depth.
        Had to setup depth to avoid infinite stack
        """
        if current_depth > max_depth or current_url in self.visited_urls:
            return

        self.visited_urls.add(current_url)
        page_content = self._fetch_page(current_url)
        if page_content is None:
            return

        sanitized_url = self._sanitize_url(current_url)
        if self._is_product_page(sanitized_url):
            self.products_urls.add(sanitized_url)
            self._write_to_file(sanitized_url)
            self._print_logs(sanitized_url)

        links = self._extract_links(page_content)
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(lambda link: self._recursive_crawl(urljoin(sanitized_url, link), current_depth + 1, max_depth), links)

    def crawl(self, max_depth=10):
        """
        Starts the crawling process up to the specified depth.
        """
        if not self._is_valid(self.url):
            print(f"Skipping {self.url} due to invalid URL.")
            return
        self._recursive_crawl(self.url, 0, max_depth)
