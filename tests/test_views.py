# Standard Imports
import requests


# Globals
IMATCH_URL = "http://localhost:8099"
TIMEOUT = 10


# Define Tests
def test_ping_handler():
    response = requests.get(f"{IMATCH_URL}/ping")
    assert response
    assert response.status_code == 200


def test_add_handler():
    response = requests.post(
        f'{IMATCH_URL}/add',
        data={
            'url': 'https://ichef.bbci.co.uk/news/800/cpsprodpb/15665/production/_107435678_perro1.jpg',
            'filepath': f'testing_add1',
            'metadata': {'testing': 'add_method'}
        },
        timeout=TIMEOUT
    )
    assert response.status_code == 200


def test_delete_handler():
    pass


def test_search_handler():
    pass


def test_count_handler():
    pass


def test_list_handler():
    pass
