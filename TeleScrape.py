#!/usr/bin/env python3
"""
TeleScrape Version 1.2 (Updated Production): A sophisticated web scraping tool designed for extracting content
from Telegram channels, with enhanced privacy features through Tor network integration,
a dashboard for displaying results, including matched content based on specified keywords,
and extended functionality to keep running until manually stopped and log total execution time.

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

# Global variables to store links info, results, and keywords
links_info = {'count': 0, 'filename': ''}
results = []
keywords_searched = []
lock = Lock()

# Configure logging to output to both console and file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    handlers=[
                        logging.FileHandler("TeleScrape.log"),
                        logging.StreamHandler()
                    ])

def setup_chrome_with_tor():
    """Setups Chrome with Tor proxy for enhanced privacy."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--proxy-server=socks5://localhost:9050")
    chromedriver_path = "/usr/local/bin/chromedriver"
    chrome_service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    return driver

def verify_tor_connection():
    """Verifies the connection to the Tor network."""
    session = requests.session()
    session.proxies = {'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'}
    try:
        ip_check_url = 'http://httpbin.org/ip'
        response = session.get(ip_check_url)
        tor_ip = response.json()["origin"]
        logging.info(f"Connected to TOR.\nTOR IP Address: {tor_ip}")
    except requests.RequestException as e:
        logging.error(f"Tor connection failed: {e}")

def get_current_datetime_formatted():
    """Returns the current date and time formatted as a string."""
    return datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")

def read_keywords_from_file(file_path):
    """Reads keywords from a specified file."""
    global keywords_searched
    try:
        with open(file_path, 'r') as file:
            keywords_searched = [line.strip() for line in file if line.strip()]
            return keywords_searched
    except FileNotFoundError:
        logging.error(f"Keyword file '{file_path}' not found.")
        return []

def create_links_file():
    """Fetches Telegram channel links and saves them to a file."""
    global links_info
    driver = setup_chrome_with_tor()
    try:
        github_url = "https://github.com/fastfire/deepdarkCTI/blob/main/telegram_infostealer.md"
        logging.info(f"Fetching links from {github_url}...")
        driver.get(github_url)
        time.sleep(5)  # Wait for the page to load

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        links = soup.find_all("a", href=True)
        filtered_links = [link["href"] for link in links if "https://t.me/" in link["href"]]

        current_datetime = get_current_datetime_formatted()
        links_filename = f"{current_datetime}-links.txt"
        links_info['count'] = len(filtered_links)
        links_info['filename'] = links_filename

        with open(links_filename, "w") as file:
            for link in filtered_links:
                file.write(link + "\n")

        logging.info(f"Found {len(filtered_links)} links and saved them to '{links_filename}'")
        return filtered_links
    except (WebDriverException, Exception) as e:
        logging.error(f"Error creating links file: {e}")
    finally:
        driver.quit()

def scrape_channel(channel_url, keywords):
    """Scrapes content from specified Telegram channel URL based on given keywords."""
    driver = setup_chrome_with_tor()
    try:
        channel_url_preview = channel_url if channel_url.startswith("https://t.me/s/") else channel_url.replace("https://t.me/", "https://t.me/s/")
        driver.get(channel_url_preview)
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tgme_widget_message_text")))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        text_elements = soup.find_all(class_="tgme_widget_message_text")
        for element in text_elements:
            text = element.get_text()
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    keyword_lower = keyword.lower()
                    index = text.lower().find(keyword_lower)
                    start_index = max(index - 150, 0)
                    end_index = min(index + len(keyword_lower) + 150, len(text))
                    context = text[start_index:end_index]
                    match_message = f"Match found in {channel_url}: ...{context}..."
                    with lock:
                        results.append(match_message)
                    logging.info(match_message)
                    break
    except TimeoutException:
        logging.warning(f"Timed out waiting for page to load: {channel_url}")
    except Exception as e:
        logging.error(f"Error scraping {channel_url}: {str(e)}\n{traceback.format_exc()}")
    finally:
        driver.quit()

@app.route('/')
def dashboard():
    """Flask route for the dashboard."""
    with lock:
        return render_template('dashboard.html', results=results, links_info=links_info, keywords=keywords_searched)

def run_flask_app():
    """Runs the Flask application in a separate thread."""
    app.run(debug=True, host='0.0.0.0', port=8081, use_reloader=False)

def main():
    """Main function to orchestrate the scraping process and update the dashboard."""
    start_time = time.time()  # Start time of script execution
    verify_tor_connection()
    keywords = read_keywords_from_file('keywords.txt')
    links = create_links_file()  # Fetch links from the specified source

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_channel, link, keywords) for link in links]
        concurrent.futures.wait(futures)

    end_time = time.time()  # End time of script execution
    total_time = end_time - start_time
    logging.info(f"Scraping and keyword search completed in {total_time:.2f} seconds. Please visit the dashboard for results.")

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask_app)
    flask_thread.daemon = True  # Ensure the Flask thread is daemonic and terminates when the main thread does
    flask_thread.start()

    main()

    # Keep the script running until manually stopped
    try:
        while True:
            time.sleep(1)  # Sleep for 1 second at a time to handle any KeyboardInterrupt (Ctrl+C) gracefully
    except KeyboardInterrupt:
        print("\nScript manually stopped by the user.")
