import datetime
import os
import sys

from loguru import logger


def setup_logging(self):
    today = datetime.datetime.today()
    today_str = today.strftime("%Y-%m-%d")
    log_file_name = f"{today_str}_bot_log.txt"
    log_full_path = os.path.join(LOG_DIR, log_file_name)
    open(log_full_path, 'w').close()
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>{level}</red> {message}",
               colorize=True)
    logger.add(log_full_path, format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}")