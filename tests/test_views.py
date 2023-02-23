# Standard Imports
import json
import requests
# Extra imports
import pytest
from elasticsearch import Elasticsearch


# Globals
IMATCH_URL = "http://localhost:8099"
ELASTICSEARCH_URL = "http://localhost:9200"
ELASTICSEARCH_INDEX = "imatch"

TIMEOUT = 10
URL1 = 'https://ichef.bbci.co.uk/news/800/cpsprodpb/15665/production/_107435678_perro1.jpg'
URL2 = 'https://www.clinicaveterinariaaguilar.es/wp-content/uploads/2020/01/cachorro.jpg'
es = Elasticsearch(
    [ELASTICSEARCH_URL],
    verify_certs=True,
    timeout=TIMEOUT,
    max_retries=5,
    retry_on_timeout=True
)


# Basic functions
def get_filepath(url):
    return url.split('/')[-1]


def get_metadata(url):
    return {'url': url, 'path': get_filepath(url)}


def add_photo(metadata):
    return requests.post(
        f'{IMATCH_URL}/add',
        data={
            'url': metadata['url'],
            'filepath': metadata['path'],
            'metadata': json.dumps(metadata)
        },
        timeout=TIMEOUT
    )


def search_photo(url):
    return requests.post(
        f'{IMATCH_URL}/search',
        files={'image': requests.get(url).content},
        timeout=TIMEOUT
    )


def delete_photo(url):
    return requests.delete(
        f'{IMATCH_URL}/delete',
        data={'filepath': get_filepath(url)},
        timeout=TIMEOUT
    )


def get_list():
    return requests.get(f'{IMATCH_URL}/list')


# Fixture
@pytest.fixture(autouse=True)
def run_around_tests():
    """Fixture to execute asserts before and after a test is run"""
    yield
    # Clean ElasticSearch Index
    try:
        es.delete_by_query(index=ELASTICSEARCH_INDEX, body={"query": {"match_all": {}}}, ignore=404)
    except Exception as e:
        pass


# Define Tests
def test_ping_handler():
    response = requests.get(f"{IMATCH_URL}/ping")
    assert response.status_code == 200


def test_add_handler():
    response = add_photo(get_metadata(URL1))
    assert response.status_code == 200


def test_delete_handler():
    pass


def test_search_handler():
    response_add = add_photo(get_metadata(URL2))
    assert response_add.status_code == 200
    response_search = search_photo(URL2)
    assert response_search.status_code == 200
    result = response_search.json()['result'][0]
    assert result['score'] == 100
    assert result['filepath'] == get_metadata(URL2)['path']
    import ipdb; ipdb.set_trace()
    assert result['metadata'] == get_metadata(URL2)


def test_count_handler():
    response_count = requests.get(f'{IMATCH_URL}/count')
    assert response_count.json()['result'] == 0
    add_photo(get_metadata(URL1))
    response_count = requests.get(f'{IMATCH_URL}/count')
    assert response_count.json()['result'] == 1
    add_photo(get_metadata(URL2))
    response_count = requests.get(f'{IMATCH_URL}/count')
    assert response_count.json()['result'] == 2


def test_list_handler():
    pass
