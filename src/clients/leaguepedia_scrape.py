import time
from curl_cffi import requests
from bs4 import BeautifulSoup

def scrape_deeplol_name(player_name: str) -> str | None:
    url = f"https://lol.fandom.com/wiki/{player_name}"

    time.sleep(1)

    try:
        response = requests.get(url, impersonate="chrome", timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        link = soup.find('a', href=lambda x: x and 'deeplol.gg' in x)

        if link:
            deeplol_url = link['href']
            deeplol_name = deeplol_url.rstrip('/').split('/')[-1]
            return deeplol_name

        else:
            print(f"Unable to find deeplol name on leagupedia for {player_name}")
            return None

    except Exception as e:
        print(f"Failed to get deeplol name on Leaguepedia for {player_name}: {e}")
        return None


if __name__ == "__main__":
    # Test usage
    test_players=[
        'Hans Sama',
        'frajgo',
        'mikusik',
        'non_existing'
    ]

    for player in test_players:
        result = scrape_deeplol_name(player)
        print(f"Result: {result}")