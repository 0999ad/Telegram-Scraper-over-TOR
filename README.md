# Telegram Channel Scraper and Dashboard via TOR

## Legal Disclaimer
This software is intended for **educational and research purposes only**. Users must ensure their use of this software complies with local laws and regulations. The creators of this software disclaim any liability for misuse or for any damage that may occur from using the software. It is the user's responsibility to use this software ethically and in accordance with the terms of service of any platform or data it interacts with.

## Overview

This project provides a powerful tool for scraping content from Telegram channels based on specified keywords, leveraging the Tor network for enhanced privacy. It combines the robust web scraping capabilities of Selenium with the dynamic and interactive presentation of results through a Flask-based web dashboard.

## Features

- **Tor Network Integration**: Maximizes user privacy by routing scraping actions through the Tor network.
- **Targeted Content Scraping**: Automatically retrieves content from specified Telegram channels, utilizing user-defined keywords for targeted scraping.
- **Dynamic Results Dashboard**: Features a Flask web dashboard that updates in real-time to display scraping outcomes, offering insights into the data collected.
- **Concurrent Scraping**: Implements parallel processing to scrape multiple sources simultaneously, optimizing the use of resources and reducing execution time.
- **Configurable and Extensible**: Designed for easy customization and extension, allowing users to adapt the tool to their specific needs without extensive modifications.

## Technical Specifications

### Dependencies

- Python 3.x
- Flask
- BeautifulSoup4
- Selenium
- Requests

### Installation

1. **Python 3.x**: Ensure Python 3.x is installed on your machine.
2. **Dependencies Installation**: Install necessary Python packages.
   ```sh
   pip install flask beautifulsoup4 selenium requests
   ```
3. **Tor Setup**: Install and run Tor on your local system. The software expects a Tor SOCKS proxy on `localhost:9050`.
4. **Chrome WebDriver**: Ensure Chrome WebDriver is installed and its path is correctly configured in the script.

### Structure

- `TeleScrape.py`: Main script integrating scraping logic, Flask app, and Tor configuration.
- `keywords.txt`: A simple text file listing the keywords for content filtering.
- `/templates`: Contains HTML templates for the Flask dashboard.

## Usage

1. **Configure Keywords**: Fill `keywords.txt` with the keywords you wish to use for scraping.
2. **Execute Script**: Run `TeleScrape.py` to initiate scraping and start the Flask dashboard.
   ```sh
   python TeleScrape.py
   ```
3. **Dashboard Access**: Visit `http://127.0.0.1:8081/` in your browser to view live updates of the scraping process and results.

## Dashboard Features

- **Live Updates**: The dashboard refreshes in real-time, showcasing the latest scraping results.
- **Keyword Highlighting**: Enhances readability by highlighting keywords and matches within the scraped content.
- **Responsive Design**: Ensures a seamless viewing experience across various devices and screen sizes.
<img width="1792" alt="Screenshot 2024-03-20 at 20 31 49" src="https://github.com/0999ad/Telegram-Scraper-over-TOR/assets/34707278/f757d0e6-3de6-4d10-86ac-70812f9dfa26">

## Contributing

We welcome contributions to improve the project. If you have suggestions or enhancements, please fork the repository, make your changes, and submit a pull request for review.

## License

This project is licensed under the [MIT License](LICENSE.md), encouraging a wide adoption and contribution by providing a permissive framework for software sharing and modification.
