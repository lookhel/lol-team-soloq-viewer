from fastapi import FastAPI, HTTPException

from services.champion_service import fetch_champions_data, fetch_current_ddragon_version
from src.db.database import get_connection
from src.db.repositories.competition_repo import (
    load_competition_names,
    load_competition_teams
)
from src.db.repositories.team_repo import load_team
from src.db.repositories.summoner_repo import (
    load_player_summoners,
    load_summoner_stats
)
from src.db.repositories.player_repo import load_player
from src.services.stats_service import merge_summoner_stats

app = FastAPI(title="LoL Team SoloQ Analyzer API")

@app.get('/competition-list')
def get_competitions():
    with get_connection() as conn:
        names = load_competition_names(conn)
    return {"competition_list": names}


@app.get('/competitions/{name}')
def get_competition_teams(name: str):
    with get_connection() as conn:
        teams = load_competition_teams(conn, name)

    if not teams:
        raise HTTPException(status_code=404, detail=f"Competition {name} not found")

    return {
        "competition": name,
        "teams": [
            {
                "overview_page": team.overview_page,
                "name": team.name,
                "short": team.short
            }
            for team in teams
        ]
    }


@app.get('/teams/{name}')
def get_team(name: str):
    with get_connection() as conn:
        team = load_team(conn, name)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team {name} not found")

        return {
            "overview_page": team.overview_page,
            "name": team.name,
            "short": team.short,
            "org_location": team.org_location,
            "region": team.region,
            "players": [{
                'name': player.name,
                'overview_page': player.overview_page,
                'role': player.role,
                'is_substitute': bool(player.is_substitute),
            }
                for player in team.players
            ]
        }


@app.get('/players/{name}')
def get_player(name: str):
    with get_connection() as conn:
        player = load_player(conn, name)

        if not player:
            raise HTTPException(status_code=404, detail=f"Player {name} not found")

        load_player_summoners(conn, player)

        summoner_stats_list = []

        for s in player.summoners:
            load_summoner_stats(conn, s)
            summoner_stats_list.append(s.champion_stats)

        merged = merge_summoner_stats(summoner_stats_list)

        return {
            'name': player.name,
            'overview_page': player.overview_page,
            'role': player.role,
            'is_substitute': bool(player.is_substitute),
            'summoners': [
                {
                    'puu_id': summoner.puu_id,
                    'riot_id_name': summoner.riot_id_name,
                    'riot_id_tag_line': summoner.riot_id_tag_line,
                    'platform_id': summoner.platform_id
                }
                for summoner in player.summoners
            ],
            'merged_soloq_stats': merged
        }

@app.get('/champions')
def get_champions_data():
    return fetch_champions_data(fetch_current_ddragon_version())