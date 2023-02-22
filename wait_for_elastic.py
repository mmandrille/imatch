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
ELASTICSEARCH_URL = os.environ['ELASTICSEARCH_URL']


# Run
if __name__ == "__main__":
    response = None
    while not response or response.status_code != 200:
        try:
            logger.info(f"Testing ElasticSearch Server at: {ELASTICSEARCH_URL}")
            response = requests.get(
                f"http://{ELASTICSEARCH_URL}/_cluster/health",
                timeout=TIMEOUT,
            )
            logger.info(f"Elastic Status: {response.json()}")
        except Exception as e:
            logger.info(f"Elastic is not available in {ELASTICSEARCH_URL}, keep waiting...")
            logger.debug(e)
            time.sleep(5)
