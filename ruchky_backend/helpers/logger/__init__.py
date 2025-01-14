import logging

logging.basicConfig(
    level=logging.INFO, format="%(name)s - %(levelname)s - [%(funcName)s] - %(message)s"
)
logger = logging.getLogger(__name__)
