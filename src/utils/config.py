
import os
import yaml

from .logger_config import loger_config

logger = loger_config()

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..', 'config/scraper_config.yaml')
)



def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            logger.info('Config loaded successfully.')
    else:
        config = {}
        logger.warning('Config file not found, using defaults.')
    return config