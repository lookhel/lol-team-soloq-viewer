import requests

BASE_URL = "https://ddragon.leagueoflegends.com"

def fetch_current_ddragon_version() -> str:
    url = f"{BASE_URL}/api/versions.json"

    response = requests.get(url)
    response.raise_for_status()
    versions_list = response.json()
    current_version = versions_list[0]

    return current_version

def fetch_champions_data(version: str) -> list[dict]:
    url = f"{BASE_URL}/cdn/{version}/data/en_US/champion.json"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json().get("data")

    champion_data = [
        {
            "id": champion['key'],
            "name": champion['name'],
            "image": champion['image']['full'],
            "version": champion['version'],
        }
        for champion in data.values()
    ]
    return champion_data