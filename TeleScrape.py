#!/usr/bin/env python3
"""
TeleScrape Version 6.2 (BETA): An advanced web scraping tool designed for extracting content
from Telegram channels. This version includes enhanced privacy features with Tor network integration,
a responsive dashboard for displaying results, and functionality for dynamically updating keywords.
New in this version:
- Configurable multi-site scraping with simple URL and selector setup,
- Enhanced error handling and logging capabilities,
- Use of Selenium for dynamic content sites like GitHub,
- Duplicate link removal before scraping,
- Improved system stability and performance optimization,
- Real-time updates on the dashboard using WebSocket,
- Advanced keyword matching using NLP techniques,
- Improved user feedback and real-time status updates.
.___________.  _______      _______.        _______.  ______ .______          ___      .______    _______ .______
|           | /  _____|    /       |       /       | /      ||   _  \        /   \     |   _  \  |   ____||   _  \
`---|  |----`|  |  __     |   (----`      |   (----`|  ,----'|  |_)  |      /  ^  \    |  |_)  | |  |__   |  |_)  |
    |  |     |  | |_ |     \   \           \   \    |  |     |      /      /  /_\  \   |   ___/  |   __|  |      /
    |  |     |  |__| | .----)   |      .----)   |   |  `----.|  |\  \----./  _____  \  |  |      |  |____ |  |\  \----.
    |__|      \______| |_______/       |_______/     \______|| _| `._____/__/     \__\ | _|      |_______|| _| `._____|

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
from flask import Flask, render_template, request, redirect, url_for
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import concurrent.futures
from threading import Thread, Lock
import traceback
from flask_socketio import SocketIO, emit
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app, async_mode='threading')
nltk.download('vader_lexicon')

links_info = {'count': 0, 'filename': ''}
results = []
keywords_searched = []
lock = Lock()
tor_status = {'connected': False, 'ip_address': 'N/A'}
results_filename = ""
scraping_in_progress = Lock()
scrape_start_time = None
scrape_end_time = None

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
        response = session.get(ip_check_url, timeout=10)
        tor_status['ip_address'] = response.json()["origin"]
        tor_status['connected'] = True
        logging.info(f"Connected to TOR. TOR IP Address: {tor_status['ip_address']}")
    except requests.RequestException as e:
        tor_status['connected'] = False
        logging.error(f"Tor connection failed: {e}")

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

def read_bespoke_channels():
    try:
        with open('bespoke_channels.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

def write_bespoke_channels(channels):
    with open('bespoke_channels.txt', 'w') as file:
        for channel in channels:
            file.write(f"{channel}\n")

sites_to_scrape = [
    {
        "url": "https://github.com/fastfire/deepdarkCTI/blob/main/telegram_threat_actors.md",
        "selector": "article.markdown-body a[href]",
        "use_selenium": True
    },
    {
        "url": "https://github.com/fastfire/deepdarkCTI/blob/main/telegram_infostealer.md",
        "selector": "article.markdown-body a[href]",
        "use_selenium": True
    },
    {
        "url": "https://www.breachsense.com/telegram-channels/",
        "selector": "tr a[href]",
        "use_selenium": False
    }
]
def fetch_links_from_site(url, selector, use_selenium=False):
    try:
        if use_selenium:
            driver = setup_chrome_with_tor()
            driver.get(url)
            time.sleep(5)  # Wait for the page to load fully
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
        else:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.select(selector) if "https://t.me/" in a['href']]
        return links
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return []
    except WebDriverException as e:
        logging.error(f"Selenium error with {url}: {e}")
        return []

def create_links_file():
    global links_info
    all_links = read_bespoke_channels()  # Start with bespoke channels
    for site in sites_to_scrape:
        logging.info(f"Fetching links from {site['url']}...")
        site_links = fetch_links_from_site(site['url'], site['selector'], site.get('use_selenium', False))
        all_links.extend(site_links)

    # Remove duplicates by converting to a set and back to a list
    unique_links = list(set(all_links))
    links_info['count'] = len(unique_links)
    current_datetime = get_current_datetime_formatted()
    links_filename = f"{current_datetime}-links.txt"
    links_info['filename'] = links_filename

    with open(links_filename, "w") as file:
        for link in unique_links:
            file.write(f"{link}\n")
    logging.info(f"Found {links_info['count']} unique links in total and saved them to '{links_filename}'")
    return unique_links

def create_results_file():
    global results_filename
    current_datetime = get_current_datetime_formatted()
    results_filename = f"{current_datetime}-results.txt"
    with open(results_filename, "w") as file:
        pass
    logging.info(f"Results file initialized: {results_filename}")

def scrape_channel(channel_url, keywords):
    driver = setup_chrome_with_tor()
    sia = SentimentIntensityAnalyzer()
    try:
        channel_url_preview = channel_url if channel_url.startswith("https://t.me/s/") else channel_url.replace(
            "https://t.me/", "https://t.me/s/")
        driver.get(channel_url_preview)
        WebDriverWait(driver, 120).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "tgme_widget_message_text")))

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
                    sentiment = sia.polarity_scores(context)
                    match_message = f"Keyword Match '{keyword}' found in {channel_url}: ...{context}... Sentiment: {sentiment}"
                    with lock:
                        results.append(match_message)
                        with open(results_filename, 'a') as file:
                            file.write(f"{match_message}\n*****\n\n")
                    logging.info(match_message)
                    socketio.emit('new_result', {'message': match_message})
                    break  # Break after the first keyword match per element
    except TimeoutException:
        logging.warning(f"Timed out waiting for page to load: {channel_url}")
        socketio.emit('error', {'message': f"Timed out waiting for page to load: {channel_url}"})
    except Exception as e:
        logging.error(f"Error scraping {channel_url}: {e}")
        socketio.emit('error', {'message': f"Error scraping {channel_url}: {e}"})
    finally:
        driver.quit()

@app.route('/restart-scrape', methods=['POST'])
def restart_scrape():
    if scraping_in_progress.locked():
        logging.info("Scraping process is already running and cannot be restarted.")
        return redirect(url_for('dashboard'))
    Thread(target=start_scraping).start()
    return redirect(url_for('dashboard'))

def start_scraping():
    if scraping_in_progress.locked():
        logging.info("Scraping process is already running and cannot be started again.")
        return
    global scrape_start_time, scrape_end_time
    with scraping_in_progress:
        global results, links_info, results_filename
        with lock:
            results.clear()
            links_info = {'count': 0, 'filename': ''}
        logging.info("Starting new scrape with current keywords.")
        scrape_start_time = get_current_datetime_formatted()
        keywords = keywords_searched
        links = create_links_file()
        create_results_file()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(scrape_channel, link, keywords) for link in links]
            concurrent.futures.wait(futures)
        scrape_end_time = get_current_datetime_formatted()
        logging.info("Scraping process completed.")
        socketio.emit('scrape_complete', {
            'start_time': scrape_start_time,
            'end_time': scrape_end_time,
            'total_links': links_info['count']
        })

@app.route('/update-keywords', methods=['POST'])
def update_keywords():
    new_keywords = request.form['new_keywords']
    new_keyword_list = new_keywords.split(',')
    global keywords_searched
    keywords_searched = new_keyword_list
    with open('keywords.txt', 'w') as file:
        for keyword in new_keyword_list:
            file.write(f"{keyword}\n")
    return redirect(url_for('restart_scrape'))

@app.route('/add-channel', methods=['POST'])
def add_channel():
    new_channel = request.form['new_channel'].strip()
    if new_channel:
        channels = read_bespoke_channels()
        if new_channel not in channels:
            channels.append(new_channel)
            write_bespoke_channels(channels)
    return redirect(url_for('dashboard'))

@app.route('/')
def dashboard():
    keywords_str = ' | '.join(keywords_searched)
    with lock:
        local_results = list(results)
    return render_template('dashboard.html',
                           results=local_results,
                           links_info=links_info,
                           keywords=keywords_str,
                           tor_connected=tor_status['connected'],
                           tor_ip=tor_status['ip_address'],
                           results_filename=results_filename,
                           scrape_start_time=scrape_start_time,
                           scrape_end_time=scrape_end_time,
                           warning_message="Warning: The information displayed is live and could contain offensive or malicious language.")

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@socketio.on('connect')
def test_connect():
    logging.info('Client connected')
    emit('response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    logging.info('Client disconnected')

def run_flask_app():
    socketio.run(app, debug=True, host='0.0.0.0', port=8081, use_reloader=False)

def main():
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
    start_scraping()

    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"Scraping and keyword search completed in {total_time:.2f} seconds. Please visit the dashboard for results.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Manual interruption received, exiting.")

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    main()
