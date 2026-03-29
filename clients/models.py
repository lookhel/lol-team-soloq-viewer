from dataclasses import dataclass
from typing import List, Optional


# Name, tag line and platform are sufficient to identify summoner
@dataclass
class Summoner:
    riot_id_name: str
    riot_id_tag_line: str
    platform_id: str = 'EUW1'
    puu_id: str | None = None
    champion_stats: dict | None = None

# Player can have assigned more summoners (accounts) than one
@dataclass
class Player:
    name: str
    team : str
    summoners: List[Summoner]

    def assign_summoner(self, riot_id_name: str, riot_id_tag_line: str, platform_id: str) -> None:
        self.summoners.append(Summoner(riot_id_name, riot_id_tag_line, platform_id))

@dataclass
class Team:
    name: str
    tag: Optional[str]
    team_location: Optional[str]
    region: Optional[str]
    players: List[Player]

    def assign_player(self, name):
        pass