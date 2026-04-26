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
    overview_page = player.overview_page
    name = player.name
    deeplol = DeepLolAPI()

    # 1. Scrape leaguepedia
    scraping_result = scrape_deeplol_name(overview_page)
    if scraping_result:
        deeplol_name = scraping_result[0]
        player_status = scraping_result[1]

        validate_result = deeplol.validate_player_name(deeplol_name, player_status)
        if validate_result:
            assign_deeplol(validate_result, player)
            return

    names_to_check = {name, overview_page}

    # Overview pages with names in format: nick (real name)
    if "(" in overview_page and ")" in overview_page:
        nickname, rest = overview_page.split("(", 1)

        nickname = nickname.strip()
        real_name = rest.rstrip(")").replace(" ", "_")

        transformed_name = f"{nickname}-{real_name}"
        names_to_check.add(transformed_name)


    # 2. Try to find by player name and player (transformed) overview page
    for name in names_to_check:
        validate_result = deeplol.validate_player_name(name)
        if validate_result:
            assign_deeplol(validate_result, player)
            return

    print(f"Failed to find deeplol profile for {overview_page}")
    return


def check_if_sub(player: Player) -> None:
    team = player.team.overview_page

    leaguepedia = LeaguepediaAPI()
    latest_roster = leaguepedia.fetch_latest_roster(team)

    if latest_roster:
        if {player.overview_page, player.name}.isdisjoint(latest_roster):
            player.is_substitute = True


# Test usage
if __name__ == "__main__":
    lequ = Player(name='lequ', overview_page="LeQu", team=Team(overview_page='Bomba Team'))
    hyper720 = Player(name='hyper', overview_page="Hyper720", team=Team(overview_page="Bomba Team"))
    minemaciek = Player(name='minemaciek', overview_page="Minemaciek", team=Team(overview_page="Bomba Team"))
    mikusik = Player(name='mikusik', overview_page="mikusik")
    naak_nako = Player(name='Naak Nako', overview_page="Naak Nako")

    find_deeplol_name(mikusik)
    print(mikusik.deeplol_name, mikusik.deeplol_status)

    check_if_sub(hyper720)
    check_if_sub(lequ)
    check_if_sub(minemaciek)

    print(hyper720.is_substitute, lequ.is_substitute, minemaciek.is_substitute)

    find_deeplol_name(naak_nako)
    print(naak_nako.deeplol_name, naak_nako.deeplol_status)
