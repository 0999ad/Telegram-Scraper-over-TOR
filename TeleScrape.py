#!/usr/bin/env python3
"""
TeleScrape Version 2.0 (Production): A sophisticated web scraping tool designed for extracting content
from Telegram channels, with enhanced privacy features through Tor network integration,
a dashboard for displaying results, including matched content based on specified keywords,
extended functionality to keep running until manually stopped, and ensuring the Flask dashboard remains live
for result review.

Usage:
  python TeleScrape.py
"""

import time
import requests
from bs4 import BeautifulSoup
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import datetime
from flask import Flask, render_template
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import concurrent.futures
from threading import Thread, Lock
import traceback

app = Flask(__name__, template_folder='templates')

links_info = {'count': 0, 'filename': ''}
results = []
keywords_searched = []
lock = Lock()
tor_status = {'connected': False, 'ip_address': 'N/A'}
results_filename = ""

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    handlers=[
                        logging.FileHandler("TeleScrape.log"),
                        logging.StreamHandler()
                    ])

def setup_chrome_with_tor():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--proxy-server=socks5://localhost:9050")
    chromedriver_path = "/usr/local/bin/chromedriver"
    chrome_service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return driver

def verify_tor_connection():
    session = requests.session()
    session.proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
    try:
        ip_check_url = 'http://httpbin.org/ip'
        response = session.get(ip_check_url)
        tor_status['ip_address'] = response.json()["origin"]
        tor_status['connected'] = True
        logging.info(f"Connected to TOR. TOR IP Address: {tor_status['ip_address']}")
    except requests.RequestException as e:
        logging.error(f"Tor connection failed: {e}")
        tor_status['connected'] = False

def get_current_datetime_formatted():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")

def read_keywords_from_file(file_path):
    global keywords_searched
    try:
        with open(file_path, 'r') as file:
            keywords_searched = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"Keyword file '{file_path}' not found.")
    return keywords_searched

def create_links_file():
    global links_info
    github_urls = [
        "https://github.com/fastfire/deepdarkCTI/blob/main/telegram_threat_actors.md",
        "https://github.com/fastfire/deepdarkCTI/blob/main/telegram_infostealer.md"
    ]
    all_filtered_links = []
    driver = setup_chrome_with_tor()
    try:
        for github_url in github_urls:
            logging.info(f"Fetching links from {github_url}...")
            driver.get(github_url)
            time.sleep(5)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            links = soup.find_all("a", href=True)
            filtered_links = [link["href"] for link in links if "https://t.me/" in link["href"]]
            all_filtered_links.extend(filtered_links)
    except Exception as e:
        logging.error(f"Error fetching links from {github_url}: {e}")
    finally:
        driver.quit()

    current_datetime = get_current_datetime_formatted()
    links_filename = f"{current_datetime}-links.txt"
    links_info['count'] = len(all_filtered_links)
    links_info['filename'] = links_filename

    with open(links_filename, "w") as file:
        for link in all_filtered_links:
            file.write(f"{link}\n")
    logging.info(f"Found {len(all_filtered_links)} links in total and saved them to '{links_filename}'")
    return all_filtered_links

def create_results_file():
    global results_filename
    current_datetime = get_current_datetime_formatted()
    results_filename = f"{current_datetime}-results.txt"
    with open(results_filename, "w") as file:
        pass
    logging.info(f"Results file initialized: {results_filename}")

def scrape_channel(channel_url, keywords):
    driver = setup_chrome_with_tor()
    try:
        channel_url_preview = channel_url if channel_url.startswith("https://t.me/s/") else channel_url.replace("https://t.me/", "https://t.me/s/")
        driver.get(channel_url_preview)
        WebDriverWait(driver, 120).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tgme_widget_message_text")))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        text_elements = soup.find_all(class_="tgme_widget_message_text")
        for element in text_elements:
            text = element.get_text()
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    start_index = max(text.lower().find(keyword.lower()) - 200, 0)
                    end_index = min(start_index + 200 + len(keyword), len(text))
                    context = text[start_index:end_index]
                    match_message = f"Match found in {channel_url}: ...{context}..."
                    with lock:
                        results.append(match_message)  # Append the result within the lock to ensure thread safety
                        # Write the result directly to the file
                        with open(results_filename, 'a') as file:
                            file.write(f"{match_message}\n*****\n\n")
                    logging.info(match_message)
                    break
    except TimeoutException:
        logging.warning(f"Timed out waiting for page to load: {channel_url}")
    except Exception as e:
        logging.error(f"Error scraping {channel_url}: {e}")
    finally:
        driver.quit()

@app.route('/')
def dashboard():
    """Renders the dashboard with the scraping results and status information."""
    with lock:  # Use the lock to safely access the shared results list
        local_results = list(results)  # Create a local copy to pass to the template
    return render_template('dashboard.html',
                           results=local_results,
                           links_info=links_info,
                           keywords=",".join(keywords_searched),
                           tor_connected=tor_status['connected'],
                           tor_ip=tor_status['ip_address'],
                           results_filename=results_filename,
                           warning_message="Warning: The information displayed is live and could contain offensive or malicious language.")

def run_flask_app():
    """Runs the Flask web application."""
    app.run(debug=True, host='0.0.0.0', port=8081, use_reloader=False)

def main():
    """Main function orchestrates the scraping process, initializes the Flask dashboard, and keeps the script running for user interaction."""
    start_time = time.time()
    verify_tor_connection()
    keywords = read_keywords_from_file('keywords.txt')
    if not keywords:
        logging.error("No keywords found in the file. Exiting.")
        return

    links = create_links_file()
    if not links:
        logging.error("No links were found. Exiting.")
        return

    create_results_file()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_channel, link, keywords) for link in links]
        concurrent.futures.wait(futures)

    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"Scraping and keyword search completed in {total_time:.2f} seconds. Please visit the dashboard for results.")

    # Keep the script running until manually terminated, allowing Flask dashboard to remain accessible
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Manual interruption received, exiting.")

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    main()
