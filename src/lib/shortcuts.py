import datetime
import sys
import time

import requests

from src import config


def get(url, interval=config.HTTP_REQUEST_INTERVAL, max_request=config.HTTP_MAX_REQUEST, headers=config.HTTP_HEADERS):
    """
    Custom get request. Recursively make request every designated interval.

    Args:
        url: URL link.
        interval: The delay before making requests. Default 5 seconds.
        max_request: Maximum number of request to be made. Default 999 requests.

    Returns:
        Return the http response.
    """
    time.sleep(interval)
    res = requests.get(url)
    max_request -= 1

    if res.status_code != 200 and max_request != 0:
        res = get(url, interval, max_request, headers)

    if max_request == 0:
        return None

    return res


def log(message):
    with open('mal_scraper.logs.txt', 'a') as f:
        log_time = str(datetime.datetime.now())
        f.write(f'----- {log_time} -----\n{message}\n\n')


def printd(string):
    """Print dynamically."""
    sys.stdout.write(f'\x1b[2K\r{string}')
    sys.stdout.flush()
