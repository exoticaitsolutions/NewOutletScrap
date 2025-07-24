import os
import logging
from datetime import datetime

# Setup log directory
LOG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..', 'logs')
)

# Create dated log file name
today = datetime.now().strftime('%Y-%m-%d')
LOG_FILE = os.path.join(LOG_DIR, f'news_scraper_{today}.log')


def loger_config():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    logger = logging.getLogger(__name__)
    return logger
