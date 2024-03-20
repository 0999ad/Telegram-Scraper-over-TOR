# Telegram Channel Scraper and Dashboard Via TOR

## Legal Disclaimer
This script is provided for **educational purposes only**. Users are responsible for ensuring that their use of the script complies with local legal laws and regulations. The originator of this code disclaims any responsibility for unethical or illegal use of the script. Users should exercise due diligence and respect the terms of service and data usage policies of the websites they interact with using this script.

## Overview

This advanced Python-based project is designed for scraping content from specified Telegram channels using predefined keywords, with enhanced privacy through Tor network integration. It showcases the capabilities of Selenium for robust web scraping and Flask for serving a dynamic web-based dashboard.

## Features

- **Enhanced Privacy with Tor Integration**: Routes scraping activities through the Tor network for increased anonymity.
- **Automated Telegram Channel Scraping**: Programmatically extracts data from specified Telegram channel URLs.
- **Keyword Filtering with Advanced Matching**: Employs a list of predefined keywords to filter content, supporting complex matching strategies.
- **Dynamic Flask Web Dashboard**: Displays real-time scraping results on a web dashboard, with updates as new data is scraped.
- **Parallel Scraping Mechanism**: Utilizes Python's concurrent futures for efficient scraping of multiple channels simultaneously.
- **File-Based Configuration and Data Management**: Manages keywords, results, and configurations through external text files for flexibility and persistence.

## Technical Details

### Dependencies

- Python 3.x
- Flask (`flask`)
- BeautifulSoup4 (`beautifulsoup4`)
- Selenium (`selenium`)
- Requests (`requests`)

### File Structure

- `TeleScrape.py`: The main Python script for scraping, Flask server setup, and Tor integration.
- `config.txt`: Optional configuration file for custom Flask settings and other preferences.
- `keywords.txt`: Text file containing the list of keywords for scraping, one keyword per line.
- `/templates`: Directory containing Flask HTML templates for the dashboard.

### Setup and Installation

1. **Environment Preparation**: Ensure Python 3.x is installed. Optionally, set up a virtual environment for the project.
2. **Dependencies Installation**: Install the required Python libraries.
   ```bash
   pip install flask beautifulsoup4 selenium requests
   ```
3. **Tor Configuration**: Ensure Tor is installed and running on your system. The script is configured to connect to Tor on `localhost:9050`.
4. **Chrome WebDriver Setup**: Download and place the Chrome WebDriver in your system's PATH or specify its location in the script.

### Usage

1. **Prepare Keyword File**: Populate `keywords.txt` with your target keywords for scraping.
2. **Run the Script**: Launch the script to start scraping and the Flask dashboard.
   ```bash
   python TeleScrape.py
   ```
3. **Access the Dashboard**: Navigate to `http://127.0.0.1:8080/` in a web browser to view the live scraping results.

## Flask Dashboard

The Flask dashboard serves as a real-time interface to monitor scraping results. It dynamically updates to display the latest data as the script processes Telegram channels.

### Dashboard Features

- **Real-Time Data Visualization**: Instantly displays scraping results as they are gathered.
- **Keyword and Match Highlighting**: Highlights the keywords and matched content for easy analysis.
- **Adaptive and Responsive Design**: Ensures compatibility across different devices and screen sizes.

<img width="1790" alt="Screenshot 2024-03-20 at 19 22 02" src="https://github.com/0999ad/Telegram-Scraper-over-TOR/assets/34707278/ef974a23-74f5-41f5-a897-ceffadae8d9b">

## Contributing

Contributions are highly appreciated. To contribute:

1. **Fork the Repository**: Create your copy of the project.
2. **Implement Changes**: Work on improvements or new features.
3. **Submit a Pull Request**: Propose your enhancements for integration.

## License

This project is released under the [MIT License](LICENSE.md), promoting open and permissive software licensing.

---
