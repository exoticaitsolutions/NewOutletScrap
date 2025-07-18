import os
import logging

LOG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..', 'logs')
)

LOG_FILE = os.path.join(LOG_DIR, 'news_scraper.log')


def loger_config():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    logger = logging.getLogger(__name__)
    return logger