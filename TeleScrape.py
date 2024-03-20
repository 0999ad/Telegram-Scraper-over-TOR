#!/usr/bin/env python3
"""
TeleScrape Version 1.3: A sophisticated web scraping tool designed for extracting content
from Telegram channels, with enhanced privacy features through Tor network integration.

Usage:
  python telescrape.py
"""

import time
import requests
from bs4 import BeautifulSoup
import re
import os
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

app = Flask(__name__, template_folder='templates')

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
    session = requests.session()
    session.proxies = {'http': 'socks5h://localhost:9050',
                       'https': 'socks5h://localhost:9050'}
    try:
        ip_check_url = 'http://httpbin.org/ip'
        response = session.get(ip_check_url)
        tor_ip = response.json()["origin"]
        print(f"Connected to TOR.\nTOR IP Address: {tor_ip}")
    except requests.RequestException as e:
        print(f"Tor connection failed: {e}")

def get_current_datetime_formatted():
    return datetime.datetime.now().strftime("%y-%m-%d-%H%M%S")

def read_flask_configurations():
    flask_config = {}
    try:
        with open("config.txt", "r") as config_file:
            for line in config_file:
                key, value = line.strip().split("=")
                flask_config[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Config file 'config.txt' not found. Using default configurations.")
    except Exception as e:
        print(f"Error reading config file: {e}")
    return flask_config

flask_configurations = read_flask_configurations()
app.secret_key = flask_configurations.get("SECRET_KEY", "supersecretkey")
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def dashboard():
    results_filename = flask_configurations.get("RESULTS_FILENAME", "No file")
    keywords = read_keywords_from_file('keywords.txt')
    content = "No results available."
    if results_filename and os.path.exists(results_filename):
        with open(results_filename, "r") as file:
            content = file.read()
    return render_template('dashboard.html', content=content, keywords=", ".join(keywords))

def create_results_file(keywords_input):
    current_datetime = get_current_datetime_formatted()
    results_filename = f"{current_datetime}-results-{keywords_input}.txt"
    with open(results_filename, "w") as result_file:
        result_file.write(f"{current_datetime}-results-{keywords_input}\n")
    flask_configurations["RESULTS_FILENAME"] = results_filename
    return results_filename

def read_keywords_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Keyword file '{file_path}' not found.")
        return []

def create_links_file():
    driver = setup_chrome_with_tor()
    try:
        github_url = "https://github.com/fastfire/deepdarkCTI/blob/main/telegram.md"
        driver.get(github_url)
        time.sleep(5)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        links = soup.find_all("a", href=True)
        filtered_links = [link["href"] for link in links if link["href"].startswith("https://t.me/")]

        current_datetime = get_current_datetime_formatted()
        links_filename = f"{current_datetime}-links.txt"

        with open(links_filename, "w") as file:
            for link in filtered_links:
                file.write(link + "\n")

        print(f"Found {len(filtered_links)} links and saved them to '{links_filename}'")
        return links_filename
    except (WebDriverException, Exception) as e:
        logging.error(f"Error creating links file: {e}")
        print(f"Error creating links file: {e}")
        return None
    finally:
        driver.quit()

def write_results_to_file(message_text, channel_url, keywords):
    try:
        results_filename = flask_configurations.get("RESULTS_FILENAME", "No file")
        with open(results_filename, "a", encoding='utf-8') as file:
            for keyword in keywords:
                # Find all occurrences of the keyword and surrounding 50 chars
                for match in re.finditer(r'.{0,50}' + re.escape(keyword) + r'.{0,50}', message_text, re.IGNORECASE):
                    snippet = match.group(0)
                    file.write(f"Keyword matched: {keyword}, Site: {channel_url}, Match(es): {snippet}\n")
        print(f"Keyword(s) found in {channel_url} (Written to {results_filename})")
    except Exception as e:
        logging.error(f"Error writing results to file: {e}")
        print(f"Error writing results to file: {e}")


def check_preview_channel(channel_url, keywords, timeout=60):
    driver = setup_chrome_with_tor()
    try:
        channel_url_preview = f"https://t.me/s/{channel_url.split('/')[-1]}" if not channel_url.startswith("https://t.me/s/") else channel_url
        driver.get(channel_url_preview)
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_widget_message_text")))
        except TimeoutException:
            print(f"Timed out waiting for page to load: {channel_url_preview}")
            return None, channel_url_preview

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        preview_text = soup.get_text()
        matching_keywords = [keyword for keyword in keywords if re.search(re.escape(keyword), preview_text, re.IGNORECASE)]

        if matching_keywords:
            return preview_text, channel_url_preview
        return None, channel_url_preview
    except Exception as e:
        logging.error(f"Error checking preview channel: {e}")
        print(f"Error checking preview channel: {e}")
        return None, channel_url
    finally:
        driver.quit()

def scrape_channel(channel_url, keywords):
    preview_text, updated_channel_url = check_preview_channel(channel_url, keywords)
    if preview_text:
        write_results_to_file(preview_text, updated_channel_url, keywords)
    else:
        logging.error(f"Preview not available or keyword(s) not found in {updated_channel_url}, skipping...")

def main():
    verify_tor_connection()  # Verify Tor connection before starting the scraping process
    keyword_file = 'keywords.txt'
    keywords = read_keywords_from_file(keyword_file)
    if not keywords:
        print("No keywords found. Exiting.")
        return

    results_filename = create_results_file("_".join(keywords))

    from threading import Thread
    def run_app():
        app.run(host='0.0.0.0', port=8081, debug=True, use_reloader=False)
    Thread(target=run_app).start()

    links_filename = create_links_file()
    if not links_filename:
        return

    with open(links_filename, "r") as file:
        channel_urls = file.read().splitlines()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(scrape_channel, channel_url, keywords) for channel_url in channel_urls]
            concurrent.futures.wait(futures)

    print("Scraping and keyword search completed. Please visit the dashboard for results.")

if __name__ == "__main__":
    logging.basicConfig(filename='scraping.log', level=logging.ERROR)  # Configure error logging
    main()

