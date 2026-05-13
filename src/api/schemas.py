from pydantic import BaseModel, Field

class CompetitionsResponse(BaseModel):
    competitions: list[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "competitions": [
                        "LEC 2026 Spring Playoffs",
                        "Rift Legends 2026 Spring"
                    ]
                }
            ]
        }
    }

class TeamShort(BaseModel):
    overview_page: str
    name: str
    short: str

class CompetitionTeamsResponse(BaseModel):
    name: str
    teams: list[TeamShort]
    overview_page: str
    role: str
    is_substitute: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "competition": "LEC 2026 Spring Playoffs",
                    "teams": [
                        {
                            "overview_page": "G2 Esports",
                            "name": "G2 Esports",
                            "short": "G2"
                        },
                        {
                            "overview_page": "GIANTX",
                            "name": "GIANTX",
                            "short": "GX"
                        },
                        {
                            "overview_page": "Karmine Corp",
                            "name": "Karmine Corp",
                            "short": "KC"
                        },
                        {
                            "overview_page": "Movistar KOI",
                            "name": "Movistar KOI",
                            "short": "MKOI"
                        },
                        {
                            "overview_page": "Natus Vincere",
                            "name": "Natus Vincere",
                            "short": "NAVI"
                        },
                        {
                            "overview_page": "Team Vitality",
                            "name": "Team Vitality",
                            "short": "VIT"
                        }
                    ]
                }
            ]
        }
    }

class PlayerShort(BaseModel):
    name: str
    overview_page: str
    role: str
    is_substitute: bool

class TeamResponse(BaseModel):
    overview_page: str
    name: str
    short: str
    org_location: str
    region: str
    players: list[PlayerShort]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "overview_page": "G2 Esports",
                    "name": "G2 Esports",
                    "short": "G2",
                    "org_location": "Germany",
                    "region": "EMEA",
                    "players": [
                        {
                            "name": "BrokenBlade",
                            "overview_page": "BrokenBlade",
                            "role": "Top",
                            "is_substitute": False
                        },
                        {
                            "name": "SkewMond",
                            "overview_page": "SkewMond",
                            "role": "Jungle",
                            "is_substitute": False
                        },
                        {
                            "name": "Caps",
                            "overview_page": "Caps",
                            "role": "Mid",
                            "is_substitute": False
                        },
                        {
                            "name": "Hans Sama",
                            "overview_page": "Hans Sama",
                            "role": "Bot",
                            "is_substitute": False
                        },
                        {
                            "name": "Labrov",
                            "overview_page": "Labrov",
                            "role": "Support",
                            "is_substitute": False
                        }
                    ]
                }
            ]
        }
    }

class Summoner(BaseModel):
    puu_id: str
    riot_id_name: str
    riot_id_tag_line: str
    platform_id: str

class PlayerResponse(BaseModel):
    name: str
    overview_page: str
    role: str
    is_substitute: bool
    summoners: list[Summoner]
    merged_soloq_stats: list[dict]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Caps",
                    "overview_page": "Caps",
                    "role": "Mid",
                    "is_substitute": False,
                    "summoners": [
                        {
                            "puu_id": "Bb4il9b8h3m6Jf0X4E1IdO55PKEtmUX-ghu7oS4Y4RqPzmsB21NadvjAf08Kf-JtL34TVlbWKjeB7w",
                            "riot_id_name": "g2caps",
                            "riot_id_tag_line": "1323",
                            "platform_id": "EUW1"
                        }
                    ],
                    "merged_soloq_stats": [
                        {
                            "champion_id": 0,
                            "games": 535,
                            "wins": 312,
                            "losses": 223,
                            "win_rate": 58.32,
                            "kills": 7.51,
                            "assists": 6.57,
                            "deaths": 6.09,
                            "kda": 2.31,
                            "damage_dealt_per_min": 1027.57,
                            "damage_taken_per_min": 1011.37,
                            "cs_per_min": 7.56,
                            "gold_diff_15": 705.36,
                            "cs_15": 122.41,
                            "gold_per_team": 20.66,
                            "damage_per_team": 26.01
                        },
                        {
                            "champion_id": 893,
                            "games": 85,
                            "wins": 51,
                            "losses": 34,
                            "win_rate": 60,
                            "kills": 9.92,
                            "assists": 6.33,
                            "deaths": 6.65,
                            "kda": 2.44,
                            "damage_dealt_per_min": 1241.2,
                            "damage_taken_per_min": 1101.08,
                            "cs_per_min": 7.02,
                            "gold_diff_15": 1137.75,
                            "cs_15": 118.53,
                            "gold_per_team": 20.94,
                            "damage_per_team": 29.28
                        },
                        {
                            "champion_id": 103,
                            "games": 62,
                            "wins": 37,
                            "losses": 25,
                            "win_rate": 59.68,
                            "kills": 8.16,
                            "assists": 7.16,
                            "deaths": 5.31,
                            "kda": 2.89,
                            "damage_dealt_per_min": 1118.98,
                            "damage_taken_per_min": 928.19,
                            "cs_per_min": 8.08,
                            "gold_diff_15": 846.1,
                            "cs_15": 130.74,
                            "gold_per_team": 21.52,
                            "damage_per_team": 29.1
                        },
                    ]
                }
            ]
        }
    }

class ChampionsResponse(BaseModel):
    id: int
    name: str
    image: str
    version: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                [
                    {
                        "id": 266,
                        "name": "Aatrox",
                        "image": "Aatrox.png",
                        "version": "16.10.1"
                    },
                    {
                        "id": 103,
                        "name": "Ahri",
                        "image": "Ahri.png",
                        "version": "16.10.1"
                    }
                ]
            ]
        }
    }