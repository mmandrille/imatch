# Standard Imports
import os
import time
import logging
import requests

# =============================================================================
# Logger
LOG_LEVEL = int(os.getenv('DEBUG_LEVEL', logging.INFO))
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s|%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Globals
TIMEOUT = int(os.getenv('TIMEOUT', 60))
IMATCH_URL = os.environ['IMATCH_URL']


# Run
if __name__ == "__main__":
    response = None
    while not response or response.status_code != 200:
        try:
            logger.info(f"Testing Imatch Server at: {IMATCH_URL}")
            response = requests.get(
                f"{IMATCH_URL}/ping",
                timeout=TIMEOUT,
            )
            logger.info(f"Imatch: {response.json()}")
        except Exception as e:
            logger.info(f"Imatch is not available in {IMATCH_URL}, keep waiting...")
            logger.debug(e)
            time.sleep(5)
