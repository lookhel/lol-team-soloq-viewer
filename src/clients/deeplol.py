import requests
from typing import Self
from datetime import datetime, timedelta

from src.models import Summoner, Player


class DeepLolAPI:
    BASE_URL = 'https://b2c-api-cdn.deeplol.gg'
    _current_season = None

    def __init__(self) -> None:
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> Self:
        if DeepLolAPI._current_season is None:
            self.fetch_current_season()
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

    def fetch_summoner_champion_stats(self, summoner: Summoner, season: int = None) -> None:
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

        unwanted_keys = ["ai_score", "stats_by_enemy"]
        filtered_stats = [
            {k: v for k, v in champion.items() if k not in unwanted_keys} for champion in champion_stats
        ]

        summoner.champion_stats = filtered_stats

    def fetch_summoners_for_player(self, player: Player, max_last_game_days: int = 90):
        url = f"{DeepLolAPI.BASE_URL}/summoner/strm_pro_info"

        if player.deeplol_name:
            deeplol_name = player.deeplol_name

        else:
            deeplol_name = player.name

        params= {
            'name': deeplol_name,
            'status': 'pro'
        }

        response = self.session.get(url, params=params)

        data = response.json()

        if data.get("status") is None:
            params['status'] = 'streamer'
            response = requests.get(url, params=params)
            data = response.json()
            if data.get("status") is None:
                raise ValueError(f"{player} profile on deeplol not available")

        accounts = data.get('account_list')

        if accounts is None:
            raise ValueError(f"No summoners found for {player} on deeplol")

        threshold = int((datetime.now() - timedelta(days=max_last_game_days)).timestamp())

        summoners = [
            Summoner(
                riot_id_name=acc["riot_id"],
                riot_id_tag_line=acc["riot_tag"],
                platform_id=acc["platform_id"],
                puu_id=acc["puu_id"]
            )
            for acc in accounts if acc["last_game_date"] > threshold # Assigning only active accounts
        ]

        for s in summoners:
            player.assign_summoner(s)