import logging
import random
import time
import tomllib
from pathlib import Path

from src.clients.deeplol import DeepLolAPI
from src.clients.leaguepedia_api import LeaguepediaAPI
from src.db.database import init_db, get_connection
from src.db.repositories.champion_repo import get_stored_ddragon_version, save_champions
from src.db.repositories.competition_repo import save_competition, load_competition_teams
from src.db.repositories.player_repo import (update_deeplol_profile, get_players_needing_deeplol_check,
                                             mark_deeplol_checked, get_players_needing_summoners_update,
                                             mark_summoners_checked)
from src.db.repositories.summoner_repo import (
    save_summoner_stats,
    save_player_summoners,
    get_summoners_needing_stats_update
)
from src.db.repositories.team_repo import save_team_with_roster
from src.services.champion_service import fetch_latest_ddragon_version, fetch_champions_data
from src.services.player_service import find_deeplol_name
from src.services.team_service import check_team_subs

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', encoding='utf-8',
                    level=logging.DEBUG)

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config.toml"


def refresh_competition_data(competition_name: str) -> None:
    logger.info("Starting refreshing competition data for %s", competition_name)
    leaguepedia = LeaguepediaAPI()
    teams = []

    try:
        teams = leaguepedia.fetch_competition_teams(competition_name)
    except Exception as e:
        logger.exception("Failed to fetch teams from %s: %s", competition_name, e)
        with get_connection() as conn:
            teams = load_competition_teams(conn, competition_name)

    try:
        leaguepedia.fetch_teams_rosters(teams)
    except Exception as e:
        logger.exception("Failed to fetch %s rosters: %s", competition_name, e)
        return

    with get_connection() as conn:
        for team in teams:
            try:
                check_team_subs(team)
            except Exception as e:
                logger.exception("Failed to check %s substitute players: %s", team, e)
            save_team_with_roster(conn, team)
        save_competition(conn, competition_name, teams)

    logger.info("Finished refreshing competition data for %s", competition_name)


def refresh_competitions_data(competitions: list[str]):
    for competition in competitions:
        refresh_competition_data(competition)


def refresh_deeplol_names(limit: int, max_age_days: int) -> None:
    logging.info("Checking if someone needs deeplol update")

    with get_connection() as conn:
        players_to_refresh = get_players_needing_deeplol_check(conn, limit, max_age_days)

        if not players_to_refresh:
            logging.info("All players have up to date deeplol info")
            return

        success_counter = 0
        for player in players_to_refresh:
            try:
                if find_deeplol_name(player):
                    update_deeplol_profile(conn, player)
                else:
                    mark_deeplol_checked(conn, player)

                success_counter += 1
            except Exception as e:
                logging.exception("Failed to refresh deeplol profile for %s", player)

            time.sleep(random.uniform(1, 3))

        logging.info("Updated deeplol info for %d/%d players", success_counter, len(players_to_refresh))


def refresh_summoners_for_players(limit: int, max_age_hours: int) -> None:
    logging.info("Checking if someone needs summoners update")

    with get_connection() as conn:
        players_to_refresh = get_players_needing_summoners_update(conn, limit, max_age_hours)

        if not players_to_refresh:
            logging.info("All players have up to date summoners")
            return

        success_count = 0
        with DeepLolAPI() as deeplol:
            for player in players_to_refresh:
                try:
                    deeplol.fetch_summoners_for_player(player)
                    save_player_summoners(conn, player)
                    mark_summoners_checked(conn, player)

                    success_count += 1
                except Exception as e:
                    logging.exception("Failed to refresh summoners for %s", player)

                time.sleep(random.uniform(0.2, 0.8))

        logging.info("Updated summoners info for %d/%d players", success_count, len(players_to_refresh))


def refresh_summoners_stats(limit: int, max_age_hours: int) -> None:
    with get_connection() as conn:
        summoners_to_refresh = get_summoners_needing_stats_update(conn, limit, max_age_hours)

        if not summoners_to_refresh:
            logging.info("All summoners have up to date summoners statistics")
            return

        success_count = 0
        with DeepLolAPI() as deeplol:
            for summoner in summoners_to_refresh:
                try:
                    deeplol.fetch_summoner_champion_stats(summoner)
                    save_summoner_stats(conn, summoner)

                    success_count += 1
                except Exception as e:
                    logging.exception("Failed to refresh summoner stats for %s", summoner)

                time.sleep(random.uniform(0.2, 0.8))

        logging.info("Updated summoner stats for %d/%d summoners", success_count, len(summoners_to_refresh))


def refresh_champions() -> None:
    logging.info("Checking if champions data need update")
    try:
        latest_version = fetch_latest_ddragon_version()
    except Exception as e:
        logging.exception("Failed to fetch latest ddragon version: %s", e)
        return

    with get_connection() as conn:
        stored_version = get_stored_ddragon_version(conn)
        if stored_version == latest_version:
            logging.info("Champions data is up to date for version: %s", latest_version)
            return
        try:
            data = fetch_champions_data(latest_version)
        except Exception as e:
            logging.exception("Failed to fetch champions data: %s", e)
            return
        save_champions(conn, data)
        logging.info("Updated champions data for version %s", latest_version)
        return


def main():
    init_db()

    with open(CONFIG_FILE, 'rb') as f:
        config = tomllib.load(f)
    competition_names = config['competitions']

    print(config)
    refresh_champions()
    refresh_competitions_data(competition_names)
    refresh_deeplol_names(20, 7)
    refresh_summoners_for_players(100, 24)
    refresh_summoners_stats(100, 3)


if __name__ == "__main__":
    main()
