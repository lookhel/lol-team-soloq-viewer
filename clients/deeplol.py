import requests
from typing import Self

from .models import Summoner

class DeepLolAPI:
    BASE_URL = 'https://b2c-api-cdn.deeplol.gg'
    _current_season = None

    def __init__(self) -> None:
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def fetch_current_season(self) -> None:
        url = f'{DeepLolAPI.BASE_URL}/common/season-list'

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            DeepLolAPI._current_season = int(data['season_list'][0])

        except requests.exceptions.HTTPError as e:
            raise e

    def fetch_summoner_champion_stats(self, summoner: Summoner, season: int = None) -> dict:
        if season is None:
            if DeepLolAPI._current_season is None:
                raise ValueError("current_season is not set")
            season = self._current_season

        if summoner.puu_id is None:
            summoner.puu_id=self.fetch_summoner_puu_id(summoner)

        url = f'{DeepLolAPI.BASE_URL}/summoner/champion-stat'
        params = {
            "puu_id": summoner.puu_id,
            "season": season,
            "platform_id": summoner.platform_id,
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        champion_stats = data.get('counter_champion_stats', {}).get('total').get('enemy_champion_stats').get('All')

        return champion_stats

    def fetch_summoner_puu_id(self, summoner:  Summoner) -> str:
        url = f'{DeepLolAPI.BASE_URL}/summoner/summoner'
        params = {
            'platform_id': summoner.platform_id,
            'riot_id_name': summoner.riot_id_name,
            'riot_id_tag_line': summoner.riot_id_tag_line
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        info = response.json()
        puu_id = info.get('summoner_basic_info_dict', {}).get('puu_id')

        return puu_id