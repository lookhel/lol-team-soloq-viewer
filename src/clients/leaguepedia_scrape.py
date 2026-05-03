import time
from typing import Literal
from bs4 import BeautifulSoup
from curl_cffi import requests, Response
import logging

from curl_cffi.requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=3))
def get_html(url: str) -> Response:
     return requests.get(url, impersonate="chrome", timeout=10)


def scrape_deeplol_name(player_name: str) -> tuple[str, Literal["pro", "streamer"]] | None:
    formatted_name = player_name.replace(' ', '_')

    url = f"https://lol.fandom.com/wiki/{formatted_name}"

    try:
        response = get_html(url)
        response.raise_for_status()

    except RequestException as e:
        logger.error("Error occured while fetching Leaguepedia page for %s", player_name)
        logger.error(f"Error: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    deeplol_link = soup.find('a', href=lambda x: x and 'deeplol.gg' in x)

    if deeplol_link:
        deeplol_url = deeplol_link['href']
        url_splitted = deeplol_url.rstrip('/').split('/')
        deeplol_name = url_splitted[-1]
        deeplol_status = url_splitted[-2]
        if deeplol_status not in ["pro", "streamer"]:
            return deeplol_name, "pro"
        return deeplol_name, deeplol_status

    else:
        lolpros_link = soup.find('a', href=lambda x: x and 'lolpros.gg' in x)
        if lolpros_link:
            lolpros_url = lolpros_link['href']
            url_splitted = lolpros_url.rstrip('/').split('/')
            lolpros_name = url_splitted[-1]
            return lolpros_name, "pro"

        logger.info("No deeplol name found on leaguepedia for %s", player_name)
        return None


if __name__ == "__main__":
    # Test usage
    test_players = [
        'Hans Sama',
        'frajgo',
        'mikusik',
        'non_existing'
        'Bin (Chen Ze-Bin)'
    ]

    for player in test_players:
        result = scrape_deeplol_name(player)
        print(f"Result: {result}")
