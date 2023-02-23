# Standard Imports
import os
import sys
import time
import json
import logging
# Flask imports
from flask import g as app_ctx
from flask import Flask, request, jsonify
# Extra imports
from elasticsearch import Elasticsearch
from image_match.goldberg import ImageSignature
from image_match.elasticsearch_driver import SignatureES


# =============================================================================
# Logger
LOG_LEVEL = int(os.getenv('DEBUG_LEVEL', logging.INFO))
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s|%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Globals
TIMEOUT = int(os.getenv('TIMEOUT', 60))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))
ELASTICSEARCH_URL = os.environ['ELASTICSEARCH_URL']
ELASTICSEARCH_INDEX = os.environ['ELASTICSEARCH_INDEX']
ELASTICSEARCH_DOC_TYPE = os.environ['ELASTICSEARCH_DOC_TYPE']
ALL_ORIENTATIONS = os.environ['ALL_ORIENTATIONS']


# Launch
app = Flask(__name__)
es = Elasticsearch(
    [ELASTICSEARCH_URL],
    verify_certs=True,
    timeout=TIMEOUT,
    max_retries=MAX_RETRIES,
    retry_on_timeout=True
)
ses = SignatureES(es, index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOC_TYPE)
gis = ImageSignature()
es.indices.create(index=ELASTICSEARCH_INDEX, ignore=400)


# =============================================================================
# Decorators
@app.before_request
def logging_before():
    # Store the start time for the request
    app_ctx.start_time = time.perf_counter()


@app.after_request
def logging_after(response):
    # Get total time in milliseconds
    total_time = time.perf_counter() - app_ctx.start_time
    time_in_ms = int(total_time * 1000)
    # Log the time taken for the endpoint
    logger.info('%s ms %s %s', time_in_ms, request.method, request.path)
    logger.debug('Request: %s', request.data)
    logger.debug('Response: %s', json.loads(response.get_data()))
    return response


# =============================================================================
# Helpers
def ids_with_path(path):
    matches = es.search(index=ELASTICSEARCH_INDEX,
                        _source='_id',
                        q='path:' + json.dumps(path))
    return [m['_id'] for m in matches['hits']['hits']]


def paths_at_location(offset, limit):
    search = es.search(index=ELASTICSEARCH_INDEX,
                       from_=offset,
                       size=limit,
                       _source='path')
    return [h['_source']['path'] for h in search['hits']['hits']]


def count_images():
    return es.count(index=ELASTICSEARCH_INDEX)['count']


def delete_ids(ids):
    for i in ids:
        es.delete(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOC_TYPE, id=i, ignore=404)


def dist_to_percent(dist):
    return (1 - dist) * 100


def get_image(url_field, file_field):
    if url_field in request.form:
        return request.form[url_field], False
    else:
        return request.files[file_field].read(), True


# =============================================================================
# Routes
@app.route('/add', methods=['POST'])
def add_handler():
    path = request.form['filepath']
    try:
        metadata = json.dumps(request.form['metadata'])
    except KeyError:
        metadata = None
    img, bs = get_image('url', 'image')

    old_ids = ids_with_path(path)
    ses.add_image(path, img, bytestream=bs, metadata=metadata)
    delete_ids(old_ids)

    return json.dumps({
        'status': 'ok',
        'error': [],
        'method': 'add',
        'result': []
    })


@app.route('/delete', methods=['DELETE'])
def delete_handler():
    path = request.form['filepath']
    ids = ids_with_path(path)
    delete_ids(ids)
    return json.dumps({
        'status': 'ok',
        'error': [],
        'method': 'delete',
        'result': []
    })


@app.route('/search', methods=['POST'])
def search_handler():
    img, bs = get_image('url', 'image')
    ao = request.form.get('ALL_ORIENTATIONS', ALL_ORIENTATIONS) == 'true'

    matches = ses.search_image(
            path=img,
            all_orientations=ao,
            bytestream=bs)

    return json.dumps({
        'status': 'ok',
        'error': [],
        'method': 'search',
        'result': [{
            'score': dist_to_percent(m['dist']),
            'filepath': m['path'],
            'metadata': m['metadata']
        } for m in matches]
    })


@app.route('/compare', methods=['POST'])
def compare_handler():
    img1, bs1 = get_image('url1', 'image1')
    img2, bs2 = get_image('url2', 'image2')
    img1_sig = gis.generate_signature(img1, bytestream=bs1)
    img2_sig = gis.generate_signature(img2, bytestream=bs2)
    score = dist_to_percent(gis.normalized_distance(img1_sig, img2_sig))

    return json.dumps({
        'status': 'ok',
        'error': [],
        'method': 'compare',
        'result': [{'score': score}]
    })


@app.route('/count', methods=['GET', 'POST'])
def count_handler():
    return json.dumps({
        'status': 'ok',
        'error': [],
        'method': 'count',
        'result': count_images()
    })


@app.route('/list', methods=['GET', 'POST'])
def list_handler():
    if request.method == 'GET':
        offset = max(int(request.args.get('offset', 0)), 0)
        limit = max(int(request.args.get('limit', 20)), 0)
    else:
        offset = max(int(request.form.get('offset', 0)), 0)
        limit = max(int(request.form.get('limit', 20)), 0)
    paths = paths_at_location(offset, limit)

    return json.dumps({
        'status': 'ok',
        'error': [],
        'method': 'list',
        'result': paths
    })


@app.route('/ping', methods=['GET', 'POST'])
def ping_handler():
    return json.dumps({
        'status': 'ok',
        'error': [],
        'method': 'ping',
        'result': []
    })


# =============================================================================
# Error Handling
@app.errorhandler(400)
def bad_request(e):
    return json.dumps({
        'status': 'fail',
        'error': ['bad request'],
        'method': '',
        'result': []
    }), 400


@app.errorhandler(404)
def page_not_found(e):
    return json.dumps({
        'status': 'fail',
        'error': ['not found'],
        'method': '',
        'result': []
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return json.dumps({
        'status': 'fail',
        'error': ['method not allowed'],
        'method': '',
        'result': []
    }), 405


@app.errorhandler(500)
def server_error(e):
    return json.dumps({
        'status': 'fail',
        'error': [str(e)],
        'method': '',
        'result': []
    }), 500
