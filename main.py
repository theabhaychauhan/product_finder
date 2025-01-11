from crawler import Crawler

def main():
    ecommerce_websites = [
        "https://www.amazon.in",
        "https://www.meesho.com/"
    ]
    
    all_product_urls = {}

    for url in ecommerce_websites:
        print(f"Starting crawl for: {url}")
        crawler = Crawler(url, output_file=f"{url.replace('https://', '').replace('/', '')}_product_urls.txt")
        crawler.crawl()
        all_product_urls[url] = crawler.products_urls
        print(f"Finished crawling {url}")

if __name__ == "__main__":
    main()
