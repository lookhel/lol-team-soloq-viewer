import requests
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

BASE_URL = "https://ddragon.leagueoflegends.com"

@retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
    )
def safe_get(url, **kwargs):
    return requests.get(url, timeout=10, **kwargs)

def fetch_latest_ddragon_version() -> str:
    url = f"{BASE_URL}/api/versions.json"

    response = safe_get(url)
    response.raise_for_status()
    versions_list = response.json()
    latest_version = versions_list[0]

    return latest_version

def fetch_champions_data(version: str) -> list[dict]:
    url = f"{BASE_URL}/cdn/{version}/data/en_US/champion.json"

    response = safe_get(url)
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