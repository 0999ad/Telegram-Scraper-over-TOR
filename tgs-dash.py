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


# Function to get the current date and time in the specified format
def get_current_datetime_formatted():
    return datetime.datetime.now().strftime("%y-%m-%d-%H%M%S")


# Read Flask configurations from a file (config.txt)
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


# Read Flask configurations
flask_configurations = read_flask_configurations()
app.secret_key = flask_configurations.get("SECRET_KEY", "supersecretkey")
app.config['TEMPLATES_AUTO_RELOAD'] = True


# Flask route to render the dashboard
@app.route('/')
def dashboard():
    results_filename = flask_configurations.get("RESULTS_FILENAME")
    if results_filename and os.path.exists(results_filename):
        with open(results_filename, "r") as file:
            # Read the entire content as a single string
            content = file.read()
    else:
        content = "No results available."
    return render_template('dashboard.html', content=content)


# Function to create the results.txt file with a timestamp and keywords
def create_results_file(keywords_input):
    current_datetime = get_current_datetime_formatted()
    results_filename = f"{current_datetime}-results-{keywords_input}.txt"
    with open(results_filename, "w") as result_file:
        result_file.write(f"{current_datetime}-results-{keywords_input}\n")  # Write timestamp and keywords
    # Store the filename in flask configuration for later access
    flask_configurations["RESULTS_FILENAME"] = results_filename
    return results_filename


# Function to extract links from a webpage and save them to a file
def extract_links_and_save(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")

        # Format the filename with current date and time
        current_datetime = get_current_datetime_formatted()
        formatted_output_file = f"{current_datetime}-{output_file}"

        with open(formatted_output_file, "w") as file:
            for link in links:
                href = link.get("href")
                if href and href.startswith("https://t.me/"):
                    file.write(href + "\n")

        print(f"Found {len(links)} links and saved them to '{formatted_output_file}'")
        return formatted_output_file
    except (requests.exceptions.RequestException, Exception) as e:
        error_message = f"Error extracting links: {e}"
        logging.error(error_message)
        print(error_message)
        return None


# Function to create a new links file
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


# Function to write results to a file
def write_results_to_file(message_text, channel_url, keywords_input):
    try:
        results_filename = flask_configurations.get("RESULTS_FILENAME")
        with open(results_filename, "a", encoding='utf-8') as file:
            file.write(channel_url + "\n")  # Write the channel URL
            file.write(message_text + "\n")  # Write the message text
            file.write("*" * 10 + "\n\n")  # Add 10 asterisks and two carriage returns

        print(f"Keyword(s) found in {channel_url} (Written to {results_filename})")
    except Exception as e:
        error_message = f"Error writing results to file: {e}"
        logging.error(error_message)
        print(error_message)


# Function to read results from the file with a timeout
def read_results_from_file_with_timeout(results_filename, timeout_seconds=60):
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            with open(results_filename, 'r', encoding='utf-8') as file:
                data = file.readlines()
                if data:
                    return data  # Return data if available
            time.sleep(1)  # Wait for 1 second before checking again
        except Exception as e:
            error_message = f"Error reading results from file: {e}"
            logging.error(error_message)
            print(error_message)

    # Return an empty list if timeout is reached
    return []


# Function to check if the preview channel contains any of the provided keywords
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

        # Scroll up the page
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(10):  # Adjust the range as needed
            body.send_keys(Keys.PAGE_UP)
            time.sleep(1)  # Wait for the page to load new content

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Escaping special characters in keywords
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


# Main function
def main():
    # Get keywords from the user
    keywords_input = input("Enter keywords to search for (comma-separated): ")

    # Create the results.txt file with keywords
    results_filename = create_results_file(keywords_input)

    # Start the Flask server in a different thread
    from threading import Thread
    def run_app():
        app.run(port=8080, debug=True, use_reloader=False)

    Thread(target=run_app).start()

    links_filename = create_links_file()
    if not links_filename:
        return

    time.sleep(10)  # Give some time to create the links file

    with open(links_filename, "r") as file:
        channel_urls = file.read().splitlines()

        keywords = keywords_input.split(',')

        for channel_url in channel_urls:
            print(f"Checking preview for {channel_url}")
            message_text, updated_channel_url = check_preview_channel(channel_url, keywords)
            if message_text:
                write_results_to_file(message_text, updated_channel_url, keywords_input)
            else:
                print("Preview not available or keyword(s) not found, skipping...")

    print("Scraping and keyword search completed.")


if __name__ == "__main__":
    main()
