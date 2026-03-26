from typing import Any

import requests
import json

from dataclasses import dataclass

# Test players
players = [('Cinkrof', 'sad'), ('G2 Caps', '1323')]

@dataclass
class Summoner:
    riot_id_name: str
    riot_id_tag_line: str
    platform_id: str = 'EUW1'
    puu_id: str | None = None
    champion_stats: dict | None = None

class DeepLolAPI:
    BASE_URL = 'https://b2c-api-cdn.deeplol.gg'
    current_season = None

    def __init__(self):
        self.session = requests.Session()

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fetch_current_season(self) -> None:
        url = f'{DeepLolAPI.BASE_URL}/common/season-list'
        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()
        DeepLolAPI.current_season = int(data['season_list'][0])

    def fetch_summoner_champion_stats(self, summoner: Summoner, season: int = None) -> dict:

        if season is None:
            if self.current_season is None:
                raise ValueError("current_season is not set. Call fetch_current_season() first.")
            season = self.current_season

        url = f'{DeepLolAPI.BASE_URL}/summoner/champion-stat'
        params = {
            "puu_id": summoner.puu_id,
            "season": season,
            "platform_id": summoner.platform_id,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        champion_stats = data['counter_champion_stats']['total']['enemy_champion_stats']['All']

        return champion_stats

    def fetch_summoner_puuid(self, summoner: Summoner) -> str:
        url = f'{DeepLolAPI.BASE_URL}/summoner/summoner'
        params = {
            'platform_id': summoner.platform_id,
            'riot_id_name': summoner.riot_id_name,
            'riot_id_tag_line': summoner.riot_id_tag_line
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        info = response.json()
        puu_id = info['summoner_basic_info_dict']['puu_id']

        return puu_id

"""def fetch_summoner_name(platform_id: str, puuid: str) -> str:
    url = f'{DeepLolAPI.BASE_URL}/summoner/summoner-name'
    params = {
        "platform_id": platform_id,
        "puu_id": puuid,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()"""

def main():
    with DeepLolAPI() as deeplol:
        deeplol.fetch_current_season()

        summoners = [Summoner(player[0], player[1]) for player in players]
        for s in summoners:
            s.puu_id = deeplol.fetch_summoner_puuid(s)
            s.champion_stats = deeplol.fetch_summoner_champion_stats(s)

if __name__ == "__main__":
    main()