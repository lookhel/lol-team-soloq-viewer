import time
from typing import Literal
from curl_cffi import requests
from bs4 import BeautifulSoup


def scrape_deeplol_name(player_name: str) -> tuple[str, Literal["pro", "streamer"]] | None:
    formatted_name = player_name.replace(' ', '_')

    url = f"https://lol.fandom.com/wiki/{formatted_name}"

    time.sleep(1)

    try:
        response = requests.get(url, impersonate="chrome", timeout=10)
        response.raise_for_status()

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

            else:
                print(f"Failed to find deeplol name on leagupedia for {player_name}")
                return None

    except Exception as e:
        print(f"Failed to get deeplol name on Leaguepedia for {player_name}: {e}")
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
