#!/usr/bin/env python3
"""
Web cache and tracker
"""
import requests
import redis
from functools import wraps

store = redis.Redis()


def count_url_access(method):
    """Decorator counting how many times a URL is accessed"""
    @wraps(method)
    def wrapper(url):
        cached_key = "cached:" + url
        cached_data = store.get(cached_key)
        if cached_data:
            return cached_data.decode("utf-8")

        count_key = "count:" + url
        try:
            html = method(url)
        except Exception as e:
            store.set(count_key, 0)
            raise e

        store.incr(count_key)
        store.set(cached_key, html)
        store.expire(cached_key, 10)
        return html
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Returns HTML content of a URL"""
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"Failed to retrieve URL: {url}")
    return res.text

if __name__ == "__main__":
    print(get_page("http://slowwly.robertomurray.co.uk"))
