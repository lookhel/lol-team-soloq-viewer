import requests
from datetime import datetime, timedelta
from typing import Self, Literal
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type

from src.models import Summoner, Player


class DeepLolAPI:
    BASE_URL = 'https://b2c-api-cdn.deeplol.gg'
    _current_season = None

    def __init__(self) -> None:
        self.session = requests.Session()

    def __enter__(self) -> Self:
        if DeepLolAPI._current_season is None:
            self.fetch_current_season()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self.session.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
    )
    def _safe_get(self, url, **kwargs):
        return self.session.get(url, timeout=10, **kwargs)

    def fetch_current_season(self) -> None:
        url = f'{DeepLolAPI.BASE_URL}/common/season-list'

        response = self._safe_get(url)
        response.raise_for_status()
        data = response.json()
        DeepLolAPI._current_season = int(data['season_list'][0])

    def fetch_summoner_puu_id(self, summoner: Summoner) -> str:
        url = f'{DeepLolAPI.BASE_URL}/summoner/summoner'
        params = {
            'platform_id': summoner.platform_id,
            'riot_id_name': summoner.riot_id_name,
            'riot_id_tag_line': summoner.riot_id_tag_line
        }

        response = self._safe_get(url, params=params)
        response.raise_for_status()

        info = response.json()
        puu_id = info.get('summoner_basic_info_dict', {}).get('puu_id')

        return puu_id

    def validate_player_name(self, name: str, status: Literal["pro", "streamer"] = "pro") -> tuple[str, Literal[
        "pro", "streamer"]] | None:
        url = f"{DeepLolAPI.BASE_URL}/summoner/strm_pro_info"

        if status == "pro":
            other_status = "streamer"

        elif status == "streamer":
            other_status = "pro"

        else:
            raise ValueError(f"Invalid status: {status}; must be either pro or streamer")

        params = {
            'name': name,
            'status': status
        }

        response = self._safe_get(url, params=params)

        data = response.json()
        response_status = data.get("status")
        if response_status == "":
            params['status'] = other_status
            response = requests.get(url, params=params)
            data = response.json()
            response_status = data.get("status")
            if response_status == "":
                return None

        actual_status = response_status.lower()

        return name, actual_status

    def fetch_summoner_champion_stats(self, summoner: Summoner, season: int = None) -> None:
        if season is None:
            if DeepLolAPI._current_season is None:
                raise ValueError("current_season is not set")
            season = self._current_season

        if summoner.puu_id is None:
            summoner.puu_id = self.fetch_summoner_puu_id(summoner)

        url = f'{DeepLolAPI.BASE_URL}/summoner/champion-stat'
        params = {
            "puu_id": summoner.puu_id,
            "season": season,
            "platform_id": summoner.platform_id,
        }

        response = self._safe_get(url, params=params)
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

        if not player.deeplol_name:
            raise ValueError(f"Player {player.name} has not deeplol name set")

        if player.deeplol_status:
            deeplol_status = player.deeplol_status

        else:
            deeplol_status = 'pro'

        params = {
            'name': player.deeplol_name,
            'status': deeplol_status
        }

        response = self._safe_get(url, params=params)

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
            for acc in accounts if acc["last_game_date"] > threshold  # Assigning only active accounts
        ]

        player.summoners = summoners