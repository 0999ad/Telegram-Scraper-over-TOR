# Telegram Channel Scraper and Dashboard

## Legal Disclaimer
Educational Use and Compliance with Local Laws This script is provided for educational purposes only. 
Users are responsible for ensuring that their use of the script complies with local legal laws and regulations. 
The originator of this code disclaims any responsibility for unethical or illegal use of the script. 
Users should exercise due diligence and respect the terms of service and data usage policies of the websites they interact with using this script.

## Overview

This Python-based project is designed to scrape content from specified Telegram channels using predefined keywords and display the results on a web-based dashboard. It leverages the capabilities of Selenium for web scraping and Flask for web server implementation.

## Features

- **Automated Telegram Channel Scraping**: Extracts data from predefined Telegram channel URLs.
- **Keyword Filtering**: Uses a list of predefined keywords for targeted scraping.
- **Flask Web Dashboard**: Real-time display of scraped results on a web dashboard.
- **File-Based Keyword and Data Management**: Keywords and results are managed through text files for ease of use and persistence.

## Technical Details

### Dependencies

- Python 3.x
- Flask (`flask`)
- BeautifulSoup (`beautifulsoup4`)
- Selenium (`selenium`)
- Chrome WebDriver (for Selenium)

### File Structure

- `tgs-dash.py`: The main Python script for scraping and Flask server.
- `config.txt`: Configuration file for Flask and other settings.
- `keywords.txt`: Text file containing the list of keywords, one per line.
- `/templates`: Folder containing Flask HTML templates.

### Setup and Installation

1. **Clone the Repository**: Clone this repository to your local machine.
2. **Install Dependencies**: Ensure all required Python libraries are installed.
   ```bash
   pip install flask beautifulsoup4 selenium
   ```
3. **Chrome WebDriver**: Ensure Chrome WebDriver is installed and accessible in your system's PATH.
4. **Keyword File**: Create or update `keywords.txt` with the required scraping keywords, one per line.

### Usage

1. **Run the Script**: Execute the `tgs-dash.py` script using Python.
   ```bash
   python tgs-dash.py
   ```
2. **Access Dashboard**: Open a web browser and go to `http://127.0.0.1:8080/` to view the scraping results.

## Flask Dashboard

The Flask application provides a real-time dashboard to display the scraping results. The results are read from a generated text file and displayed in an organized format on the dashboard.

### Dashboard Features:

- **Latest Results Display**: Shows the most recent scraping results.
- **Responsive Design**: The dashboard is responsive and can be viewed on various devices.

## Contributing

Contributions to this project are welcome. Feel free to fork the repository, make improvements, and submit pull requests.

## License

This project is open-sourced under the [MIT License](LICENSE.md).

---

This README provides a comprehensive guide for anyone interested in understanding, using, or contributing to your project. You can further customize it to better suit your repository's structure or additional details you want to include.
