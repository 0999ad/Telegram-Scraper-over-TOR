#!/usr/bin/env python3
"""
TeleScrape Version 1.0 (Production): A sophisticated web scraping tool designed for extracting content
from Telegram channels, with enhanced privacy features through Tor network integration and
a dashboard for displaying results, including matched content based on specified keywords.

Usage:
  python TeleScrape.py
"""

import time
import requests
from bs4 import BeautifulSoup
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
from threading import Thread

app = Flask(__name__, template_folder='templates')

# Global variables to store links info and results
links_info = {'count': 0, 'filename': ''}
results = []


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
        print(f"Connected to TOR.\nTOR IP Address: {tor_ip}")
    except requests.RequestException as e:
        print(f"Tor connection failed: {e}")


def get_current_datetime_formatted():
    """Returns the current date and time formatted as a string."""
    return datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")


def read_keywords_from_file(file_path):
    """Reads keywords from a specified file."""
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Keyword file '{file_path}' not found.")
        return []


def create_links_file():
    """Fetches Telegram channel links and saves them to a file."""
    global links_info
    driver = setup_chrome_with_tor()
    try:
        github_url = "https://github.com/fastfire/deepdarkCTI/blob/main/telegram.md"
        print(f"Fetching links from {github_url}...")
        driver.get(github_url)
        time.sleep(5)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        links = soup.find_all("a", href=True)
        filtered_links = [link["href"] for link in links if link["href"].startswith("https://t.me/")]

        current_datetime = get_current_datetime_formatted()
        links_filename = f"{current_datetime}-links.txt"
        links_info['count'] = len(filtered_links)
        links_info['filename'] = links_filename

        with open(links_filename, "w") as file:
            for link in filtered_links:
                file.write(link + "\n")

        print(f"Found {len(filtered_links)} links and saved them to '{links_filename}'")
        return filtered_links  # Return the list of links for further processing
    except (WebDriverException, Exception) as e:
        logging.error(f"Error creating links file: {e}")
        print(f"Error creating links file: {e}")
    finally:
        driver.quit()


def scrape_channel(channel_url, keywords):
    """Scrapes content from a specified Telegram channel URL based on keywords."""
    driver = setup_chrome_with_tor()
    try:
        # Ensure URL is in the correct format for previewing content
        channel_url_preview = f"https://t.me/s/{channel_url.split('/')[-1]}" if not channel_url.startswith(
            "https://t.me/s/") else channel_url
        driver.get(channel_url_preview)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tgme_widget_message_text")))

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        text_elements = soup.find_all(class_="tgme_widget_message_text")
        for element in text_elements:
            text = element.get_text()
            if any(keyword.lower() in text.lower() for keyword in keywords):
                # Append a snippet of the match
                results.append(f"Match found in {channel_url}: {text[:150]}")
                break
    except TimeoutException:
        print(f"Timed out waiting for page to load: {channel_url}")
    except Exception as e:
        print(f"Error scraping {channel_url}: {str(e)}")
    finally:
        driver.quit()


@app.route('/')
def dashboard():
    """Flask route for the dashboard."""
    return render_template('dashboard.html', results=results, links_info=links_info)


def run_flask_app():
    """Runs the Flask application in a separate thread."""
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)


def main():
    """Main function to orchestrate the scraping process and update the dashboard."""
    verify_tor_connection()
    keywords = read_keywords_from_file('keywords.txt')
    links = create_links_file()  # Fetch links from the specified source

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_channel, link, keywords) for link in links]
        concurrent.futures.wait(futures)

    print("Scraping and keyword search completed. Please visit the dashboard for results.")


if __name__ == "__main__":
    Thread(target=run_flask_app).start()
    main()
