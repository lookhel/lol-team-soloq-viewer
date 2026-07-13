import logging
from sqlite3 import Connection

from src.clients.deeplol import DeepLolAPI
from src.clients.leaguepedia_api import LeaguepediaAPI
from src.db.repositories.player_repo import load_player
from src.db.repositories.summoner_repo import load_player_summoners, load_summoner_stats
from src.services.stats_service import merge_summoner_stats
from src.models import Player, Team


logger = logging.getLogger(__name__)


def assign_deeplol(validate_result, player: Player) -> None:
    found_name = validate_result[0]
    found_status = validate_result[1]

    player.deeplol_name = found_name
    player.deeplol_status = found_status


def find_deeplol_name(player: Player) -> bool:
    overview_page = player.overview_page
    name = player.name
    deeplol = DeepLolAPI()
    leaguepedia = LeaguepediaAPI()

    def validate(deeplol_name: str):
        validate_result = deeplol.validate_player_name(deeplol_name)
        if validate_result:
            assign_deeplol(validate_result, player)
            return True
        return False

    # 1st option: API query for Leaguepedia (deeplol name and lolpros name)

    leagupedia_deeplol_name = leaguepedia.fetch_player_deeplol_name(overview_page)

    if leagupedia_deeplol_name:
        if validate(leagupedia_deeplol_name):
            return True

    leaguepedia_lolpros_name = leaguepedia.fetch_player_lolpros_name(overview_page)

    if leaguepedia_lolpros_name:
        if validate(leaguepedia_lolpros_name):
            return True

    names_to_check = {name, overview_page}

    # Reformats for overview pages with names in format: nick (real name)
    if "(" in overview_page and ")" in overview_page:
        nickname, rest = overview_page.split("(", 1)

        nickname = nickname.strip()
        real_name = rest.rstrip(")").replace(" ", "_")

        transformed_name = f"{nickname}-{real_name}"
        names_to_check.add(transformed_name)


    # 2nd option: Try to find by player name and player (transformed) overview page
    for name in names_to_check:
        if validate(name):
            return True

    logger.warning("Deeplol profile not found for %s", overview_page)
    return False

def get_player_with_stats(conn: Connection, overview_page: str) -> Player | None:
    player = load_player(conn, overview_page)

    if not player:
        return None

    load_player_summoners(conn, player)

    summoner_stats_list = []

    for s in player.summoners:
        load_summoner_stats(conn, s)
        summoner_stats_list.append(s.champion_stats)

    player.summoners_merged_stats = merge_summoner_stats(summoner_stats_list)

    return player


# Test usage
if __name__ == "__main__":
    lequ = Player(name='lequ', overview_page="LeQu", team=Team(overview_page='Bomba Team'))
    hyper720 = Player(name='hyper', overview_page="Hyper720", team=Team(overview_page="Bomba Team"))
    minemaciek = Player(name='minemaciek', overview_page="Minemaciek", team=Team(overview_page="Bomba Team"))
    mikusik = Player(name='mikusik', overview_page="mikusik")
    naak_nako = Player(name='Naak Nako', overview_page="Naak Nako")

    find_deeplol_name(mikusik)
    print(mikusik.deeplol_name, mikusik.deeplol_status)

    find_deeplol_name(naak_nako)
    print(naak_nako.deeplol_name, naak_nako.deeplol_status)

    find_deeplol_name(lequ)
    print(lequ.deeplol_name, lequ.deeplol_status)

    find_deeplol_name(minemaciek)
    print(minemaciek.deeplol_name, minemaciek.deeplol_status)
