from src.clients.leaguepedia_scrape import scrape_deeplol_name
from src.clients.deeplol import DeepLolAPI
from src.clients.leagupedia_api import LeaguepediaAPI
from src.models import Player, Team


def assign_deeplol(validate_result, player: Player) -> None:
    found_name = validate_result[0]
    found_status = validate_result[1]

    player.deeplol_name = found_name
    player.deeplol_status = found_status


def find_deeplol_name(player: Player) -> None:
    player_overview_page = player.overview_page
    player_name = player.name
    deeplol = DeepLolAPI()

    # 1. Scrape leaguepedia
    scraping_result = scrape_deeplol_name(player_overview_page)
    if scraping_result:
        deeplol_name = scraping_result[0]
        player_status = scraping_result[1]

        validate_result = deeplol.validate_player_name(deeplol_name, player_status)
        if validate_result:
            assign_deeplol(validate_result, player)
            return

    # 2. Try to find by player name
    validate_result = deeplol.validate_player_name(player_name)
    if validate_result:
        assign_deeplol(validate_result, player)
        return

    print(f"Failed to find deeplol profile for {player_name}")
    return


def check_if_sub(player: Player) -> None:
    player_overview_page = player.overview_page
    team = player.team.overview_page

    leaguepedia = LeaguepediaAPI()
    latest_roster = leaguepedia.fetch_latest_roster(team)

    if latest_roster:
        if player_overview_page not in latest_roster:
            player.is_substitute = True


# Test usage
if __name__ == "__main__":
    lequ = Player(name='lequ', overview_page="LeQu", team=Team(overview_page='Bomba Team'))
    hyper720 = Player(name='hyper', overview_page="Hyper720", team=Team(overview_page="Bomba Team"))
    mikusik = Player(name='mikusik', overview_page="mikusik")

    find_deeplol_name(mikusik)
    print(mikusik.deeplol_name, mikusik.deeplol_status)

    check_if_sub(hyper720)
    check_if_sub(lequ)

    print(hyper720.is_substitute, lequ.is_substitute)
