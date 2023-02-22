#!/bin/bash
wait-for-it.sh -t ${TIMEOUT} ${ELASTICSEARCH_URL}
gunicorn -b 0.0.0.0:${PORT} -w ${WORKER_COUNT} server:app
