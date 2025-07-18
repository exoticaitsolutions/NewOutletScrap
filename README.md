# News Scraper Project

A modular Python project to scrape multiple news websites (dynamic and static) using Selenium, Requests, and BeautifulSoup. All logs are centralized in the `logs` directory.

## Features
- Scrapes news from multiple sources (dynamic/static)
- Modular scraper classes for each site
- Centralized logging
- Configurable via YAML/JSON
- Follows Python best practices

## Tech Stack
- Python 3.8+
- Selenium (for dynamic sites)
- Requests + BeautifulSoup (for static sites)
- PyYAML (for config)
- Logging (standard library)
- webdriver-manager (for automatic ChromeDriver management)

## Project Structure
```
NewOutletScrap/
├── src/                # Source code (scrapers, utils, main)
│   ├── main.py         # Main runner
│   └── scrapers/       # Individual site scrapers
│   └── utils/          # Utility modules
├── logs/               # Centralized logs
├── config/             # Configuration files
├── tests/              # Unit/integration tests
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## Setup
1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure target sites in `config/scraper_config.yaml`
4. Run the main script:
   ```bash
   python src/main.py
   ```

## Usage
- Add new scrapers in `src/scrapers/`
- Logs are written to `logs/news_scraper.log`
- Test with:
   ```bash
   pytest tests/
   ```

## Automated ChromeDriver Management
This project uses [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) to automatically download and manage the correct version of ChromeDriver for your system. No manual downloads are required.

**If you encounter errors like `OSError: [WinError 193] %1 is not a valid Win32 application`:**
- Make sure you are using a 64-bit version of Python and Chrome.
- The code is set to always fetch the 64-bit ChromeDriver using:
  ```python
  from webdriver_manager.chrome import ChromeDriverManager
  driver = webdriver.Chrome(service=Service(ChromeDriverManager(architecture="x64").install()), options=options)
  ```
- If you ever see this error, try:
  1. Upgrading all packages:
     ```bash
     pip install --upgrade selenium webdriver-manager
     ```
  2. Deleting the ChromeDriver cache at `C:\Users\<your-username>\.wdm\drivers\chromedriver` and re-running the script.
  3. Ensuring your Chrome browser is up to date.
  4. Running your terminal as Administrator if you suspect permissions issues.

## Troubleshooting
- **WinError 193**: See above.
- **Chrome not found**: Make sure Chrome is installed and on your system PATH.
- **Permission errors**: Try running your terminal as Administrator.
- **Antivirus issues**: Some antivirus software may block ChromeDriver. Temporarily disable if needed.

## License
MIT 