from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Literal

class Role(Enum):
    TOP = "Top"
    JUNGLE = "Jungle"
    MID = "Mid"
    BOT = "Bot"
    SUPPORT = "Support"

# Name and tag line are sufficient to identify summoner
class Summoner:
    def __init__(self, riot_id_name: str, riot_id_tag_line: str, platform_id: str = 'EUW1', puu_id: str | None = None) -> None:
        self.riot_id_name = riot_id_name
        self.riot_id_tag_line = riot_id_tag_line
        self.platform_id = platform_id
        self.puu_id = puu_id
        self.champion_stats = {}

    def __str__(self) -> str:
        return f"{self.riot_id_name}#{self.riot_id_tag_line}"

    def __repr__(self) -> str:
        return f"{self.riot_id_name}#{self.riot_id_tag_line} {self.puu_id}"

# Player can have assigned more summoners (accounts) than one
class Player:
    def __init__(
            self,
            name: str,
            overview_page: str,
            role: Role | str | None = None,
            team: Team | None = None,
            is_substitute: bool | None = None
    ) -> None:

        if isinstance(role, str):
            role = Role(role)

        self.name = name
        self.overview_page = overview_page
        self.role = role
        self.team = team
        self.is_substitute = is_substitute
        self.deeplol_name: str | None = None
        self.deeplol_status: Literal["pro", "streamer"] | None = None
        self.summoners: List[Summoner] = []

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Player({self.name}, {self.role}, {self.team}, {self.is_substitute})"

class Team:
    def __init__(self, overview_page: str, name: str | None = None, short: str | None = None, org_location: str | None = None, region: str | None = None) -> None:
        self.name = name
        self.overview_page = overview_page
        self.short = short
        self.org_location = org_location
        self.region = region
        self.players: list[Player] = []

    def assign_player(self, player: Player) -> None:
        self.players.append(player)
        player.team = self

    def __str__(self) -> str:
        return self.overview_page

    def __repr__(self):
        return f"Team: {self.overview_page} {self.short}"