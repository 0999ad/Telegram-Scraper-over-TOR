
# TeleScrape 
**Enhanced Telegram Channel Scraper using TOR and a Flask Dashboard for results**

## Legal Disclaimer
This software is designed solely for **educational and research purposes** and should be used with ethical considerations in mind. Users are responsible for ensuring their activities comply with local laws and regulations. The authors of this software bear no responsibility for any misuse or potential damages arising from its use. It's imperative to adhere to the terms of service of any platforms interacted with through this tool.

## Overview

TeleScrape is an advanced tool for extracting content from Telegram channels, emphasizing user privacy through Tor integration and providing real-time insights via a dynamic Flask dashboard. It eschews the need for Telegram's API by utilizing Selenium for web scraping, offering a robust solution for data gathering from public Telegram channels.

## Key Features

- **Enhanced Privacy**: Routes all scraping through the Tor network to protect user anonymity.
- **Keyword-Driven Scraping**: Fetches channel content based on user-defined keywords, focusing on relevant data extraction.
- **Interactive Web Dashboard**: Utilizes Flask to present scraping results dynamically, with real-time updates and insights.
- **Efficient Parallel Processing**: Employs concurrent scraping to expedite data collection from multiple channels simultaneously.
- **User-Friendly Customization**: Designed for easy adaptability to specific requirements, supporting straightforward modifications and extensions.

## Technical Details

### Prerequisites

- Python 3.x
- Flask
- BeautifulSoup4 - bs4
- Selenium
- Requests
- flask_socketio
- nltk
- tor

### Setting Up

1. **Python 3.x Installation**: Verify Python 3.x is installed on your system.
2. python3 --version
3. **Dependencies**: Install the required Python packages using pip.
   ```bash
   pip install flask beautifulsoup4 selenium requests pysocks flask_socketio nltk tor bs4 
   ```
4. **Tor Configuration**: Install Tor locally and ensure it's configured to run a SOCKS proxy on `localhost:9050`.
5. sudo apt install tor
      ```bash
   sudo systemctl enable tor
   sudo nano /etc/tor/torrc
   ```
7. Look for the following lines in the configuration file (uncomment if necessary and ensure the port is set to 9050
   ```bash
   sudo sudo systemctl start tor
   sudo systemctl enable tor
   ```
9. You can verify that Tor is running a SOCKS proxy on localhost:9050 by using a tool like curl. Run the following command to test:
  ```
  curl --socks5 localhost:9050 https://check.torproject.org
   ```   
If Tor is correctly configured, you should see a message indicating that you are using the Tor network.
10. **WebDriver Setup**: Ensure the Chrome WebDriver is installed and properly configured in the script's path settings.
11. To set up the Chrome WebDriver on your Ubuntu system and ensure it is properly configured in your script's path settings, follow these steps:

Step 1: Download the Chrome WebDriver
Download the WebDriver from the provided link using wget:
  ```
wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip
   ```   
Step 2: Unzip the WebDriver
Unzip the downloaded file:
  ```
unzip chromedriver-linux64.zip
   ```   
Step 3: Move the WebDriver to /usr/local/bin
Move the chromedriver to a directory that is included in your system's PATH. /usr/local/bin is a common choice:
  ```
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
   ```  
Step 4: Verify the installation by checking the version:
  ```
chromedriver --version
   ```  
### Project Structure

- `TeleScrape.py`: The main script, encapsulating the scraping logic, Flask application, and Tor setup.
- `keywords.txt`: Text file listing the keywords for content scraping.
- `/templates`: Folder containing HTML templates for the Flask-based dashboard.

## Getting Started

1. **Keyword Configuration**: Populate `keywords.txt` with your desired keywords.
2. **Script Execution**: Launch `TeleScrape.py` to start scraping and activate the Flask dashboard.
   ```bash
   python TeleScrape.py
   ```
3. **Dashboard Navigation**: Access `http://127.0.0.1:8081/` on your browser to view the scraping progress and results live.

## Dashboard Highlights

- **Real-Time Refresh**: Automatically updates to display the latest scraping data.
- **Keyword Visualization**: Keywords and matches are highlighted within the content for better clarity.
- **Adaptive Design**: Ensures a consistent experience across various devices and resolutions.

![Screenshot 2024-04-10 at 15 38 31](https://github.com/0999ad/Telegram-Scraper-over-TOR/assets/34707278/84d763a2-4058-4a7e-9e18-fe2d88876e80)

## Contributing

Contributions are highly appreciated! If you have improvements or suggestions, please fork this repository, commit your changes, and submit a pull request for review.

## License

This project is distributed under the [MIT License](LICENSE.md), fostering widespread use and contribution by providing a lenient framework for software distribution and modification.
```
