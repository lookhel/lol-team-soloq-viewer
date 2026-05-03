import logging
import time

from src.clients.leaguepedia_api import LeaguepediaAPI
from src.clients.deeplol import DeepLolAPI
from src.db.repositories.summoner_repo import (
    load_summoner_stats,
    load_player_summoners,
    save_summoner_stats,
    save_player_summoners
)
from src.db.repositories.player_repo import update_deeplol_profile, load_deeplol_profile
from src.db.repositories.competition_repo import save_competition, load_competition_teams, load_competition_names
from src.db.repositories.team_repo import save_team, load_team
from src.db.database import init_db, get_connection
from src.models import Team
from src.services.player_service import find_deeplol_name
from src.services.team_service import check_team_subs


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', encoding='utf-8', level=logging.DEBUG)

competition_names = ['Rift Legends 2026 Spring', 'LPL 2026 Split 2']

def update_competition_teams(competition_name: str, leaguepedia_api: LeaguepediaAPI) -> None:
    try:
        teams = leaguepedia_api.fetch_competition_teams(competition_name)
    except Exception as e:
        logger.exception("Failed to fetch teams from %s: %s", competition_name, e)
        return

    with get_connection() as conn:
        save_competition(conn, competition_name, teams)

def update_competition_rosters(competition_name: str, leaguepedia_api: LeaguepediaAPI) -> None:
    with get_connection() as conn:
        teams = load_competition_teams(conn, competition_name)

    try:
        leaguepedia_api.fetch_teams_rosters(teams)
    except Exception as e:
        logger.exception("Failed to fetch %s rosters: %s", competition_name, e)
        return

    with get_connection() as conn:
        for team in teams:
            try:
                check_team_subs(team)
            except Exception as e:
                logger.exception("Failed to check %s substitute players: %s", team, e)
            save_team(conn, team)

    logger.info("Updated %s competition rosters", competition_name)

def refresh_competition_data(competition_name: str) -> None:

    logger.info("Starting refreshing competition data for %s", competition_name)
    leaguepedia = LeaguepediaAPI()

    update_competition_teams(competition_name, leaguepedia)
    update_competition_rosters(competition_name, leaguepedia)

    logger.info("Finished refreshing competition data for %s", competition_name)


def main():
    init_db()
    # with get_connection() as conn:
    #     #competition_names = load_competition_names(conn)
    #     for competition in competition_names:
    #         teams = load_competition_teams(conn, competition)
    #         for team in teams:
    #             team = load_team(conn, team.overview_page)
    #             if team is not None and team.players is not None:
    #                 for player in team.players:
    #                     check_if_sub(player)
    #                     load_player_summoners(conn, player)
    #                     with DeepLolAPI() as deeplol:
    #                         for summoner in player.summoners:
    #                             print(summoner)
    #                             print("before", summoner.champion_stats)
    #                             deeplol.fetch_summoner_champion_stats(summoner)
    #                             save_summoner_stats(conn, summoner)
    #                             print("after", summoner.champion_stats)
    #                 save_team(conn, team)

    for competition in competition_names:
        refresh_competition_data(competition)


if __name__ == "__main__":
    main()
