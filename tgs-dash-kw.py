import time
import requests
from bs4 import BeautifulSoup
import re
import os
import logging
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

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
    results_filename = flask_configurations.get("RESULTS_FILENAME")
    if results_filename and os.path.exists(results_filename):
        with open(results_filename, "r") as file:
            content = file.read()
    else:
        content = "No results available."
    return render_template('dashboard.html', content=content)

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
    try:
        github_url = "https://github.com/fastfire/deepdarkCTI/blob/main/telegram.md"
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

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
                if not link.startswith("https://t.me/s/"):
                    link = f"https://t.me/s/{link.split('/')[-1]}"
                file.write(link + "\n")

        print(f"Found {len(filtered_links)} links and saved them to '{links_filename}'")
        return links_filename
    except (WebDriverException, Exception) as e:
        error_message = f"Error creating links file: {e}"
        logging.error(error_message)
        print(error_message)
        return None
    finally:
        driver.quit()

def write_results_to_file(message_text, channel_url, keywords):
    try:
        results_filename = flask_configurations.get("RESULTS_FILENAME")
        with open(results_filename, "a", encoding='utf-8') as file:
            file.write(channel_url + "\n")
            file.write(message_text + "\n")
            file.write("*" * 10 + "\n\n")

        print(f"Keyword(s) found in {channel_url} (Written to {results_filename})")
    except Exception as e:
        error_message = f"Error writing results to file: {e}"
        logging.error(error_message)
        print(error_message)

def read_results_from_file_with_timeout(results_filename, timeout_seconds=60):
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            with open(results_filename, 'r', encoding='utf-8') as file:
                data = file.readlines()
                if data:
                    return data
            time.sleep(1)
        except Exception as e:
            error_message = f"Error reading results from file: {e}"
            logging.error(error_message)
            print(error_message)

    return []

def check_preview_channel(channel_url, keywords):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        if not channel_url.startswith("https://t.me/s/"):
            channel_url_preview = f"https://t.me/s/{channel_url.split('/')[-1]}"
        else:
            channel_url_preview = channel_url

        driver.get(channel_url_preview)
        time.sleep(5)

        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(10):
            body.send_keys(Keys.PAGE_UP)
            time.sleep(1)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        escaped_keywords = [re.escape(keyword) for keyword in keywords]

        preview_text = soup.get_text()
        matching_keywords = [keyword for keyword in escaped_keywords if re.search(keyword, preview_text, re.IGNORECASE)]

        if matching_keywords:
            message_texts = soup.find_all('div', class_='tgme_widget_message_text')
            for text_element in message_texts:
                message_text = text_element.get_text()
                for keyword in matching_keywords:
                    if re.search(keyword, message_text, re.IGNORECASE):
                        return message_text, channel_url_preview

        return None, channel_url_preview
    except (WebDriverException, Exception) as e:
        error_message = f"Error checking preview channel: {e}"
        logging.error(error_message)
        print(error_message)
        return None, channel_url
    finally:
        driver.quit()

def main():
    start_time = time.time()
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

    time.sleep(10)

    with open(links_filename, "r") as file:
        channel_urls = file.read().splitlines()

        for channel_url in channel_urls:
            print(f"Checking preview for {channel_url}")
            message_text, updated_channel_url = check_preview_channel(channel_url, keywords)
            if message_text:
                write_results_to_file(message_text, updated_channel_url, "_".join(keywords))
            else:
                print("Preview not available or keyword(s) not found, skipping...")
    end_time = time.time()
    total_runtime = end_time - start_time
    print(f"Total runtime: {total_runtime:.2f} seconds")
    print("Scraping and keyword search completed.")

if __name__ == "__main__":
    main()
