import logging
import os
import sys

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger():
    logger = logging.getLogger("whatsapp_minio_bot")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Handler a archivo
    fh = logging.FileHandler(os.path.join(LOG_DIR, "bot.log"))
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Handler a stdout (visible en `docker logs`)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    return logger

logger = get_logger()