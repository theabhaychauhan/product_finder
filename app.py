from flask import Flask, render_template, request, jsonify
from crawler import Crawler
import os

app = Flask(__name__)

crawler_instance = None
crawling_active = False 

@app.route('/')
def index():
    """Render the main page with a start crawling button."""
    return render_template('index.html')

@app.route('/start_crawl', methods=['POST'])
def start_crawl():
    """Start the crawl process."""
    global crawler_instance, crawling_active
    url = request.form.get('url')
    max_depth = int(request.form.get('max_depth', 10))  # Default depth 10

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    if crawling_active:
        return jsonify({'error': 'Crawl already in progress.'}), 400

    crawler_instance = Crawler(url)
    crawling_active = True
    crawler_instance.crawl(max_depth)
    
    return jsonify({'message': 'Crawl started, check the console for progress.'}), 200

@app.route('/stop_crawl', methods=['POST'])
def stop_crawl():
    """Stop the crawl process."""
    global crawling_active
    if crawling_active:
        crawling_active = False
        return jsonify({'message': 'Crawl stopped successfully.'}), 200
    else:
        return jsonify({'error': 'Crawl not running.'}), 400

@app.route('/crawl_status')
def crawl_status():
    """Check the current crawl status."""
    if crawler_instance:
        file_path = 'product_urls.txt'

        product_urls = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                product_urls = [line.strip() for line in f.readlines()]

        return jsonify({
            'visited_urls': len(crawler_instance.visited_urls),
            'products_urls': len(crawler_instance.products_urls),
            'product_urls_in_file': product_urls
        })
    else:
        return jsonify({'error': 'Crawl not started'}), 400

if __name__ == '__main__':
    app.run(debug=True)
