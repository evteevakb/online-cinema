import logging
from logging.handlers import RotatingFileHandler
import os

logger = logging.getLogger("events")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s"
)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)


file_handler = RotatingFileHandler(
    f"{log_dir}/app.log", maxBytes=10 * 1024 * 1024, backupCount=5
)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
