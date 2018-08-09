import requests

from fb_bot.highlight_fetchers.proxy import scraper_api_key_manager
from requests.utils import quote

from fb_bot.logger import logger

SCRAPER_URL = "https://api.scraperapi.com?key={}&url={}&render={}"


def get(url, render=False):
    render = 'true' if render else 'false'

    for key in scraper_api_key_manager.get_scraper_api_keys():
        response = requests.get(
            SCRAPER_URL.format(key.code, form_url(url), render)
        )

        if response.status_code == requests.codes.forbidden:
            scraper_api_key_manager.invalidate_key(key)
            logger.log('Scrapper API key too many requests: ' + key.code, forward=True)
            continue

        if response.status_code == requests.codes.ok and not key.valid:
            scraper_api_key_manager.validate_key(key)
            logger.log('Scrapper API key reset: ' + key.code, forward=True)

        return response


def form_url(url):
    return quote(url)