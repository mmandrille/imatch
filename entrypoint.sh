#!/bin/bash
python wait_for_elastic.py
gunicorn -b 0.0.0.0:${PORT} -w ${WORKER_COUNT} server:app