from src.clients.leaguepedia_scrape import scrape_deeplol_name
from src.clients.deeplol import DeepLolAPI
from src.models import Player

def assign_after_success(validate_result, player: Player) -> None:
    found_name = validate_result[0]
    found_status = validate_result[1]

    player.deeplol_name = found_name
    player.deeplol_status = found_status

def find_deeplol_name(player: Player) -> None:
    player_name = player.name
    deeplol = DeepLolAPI()

    # 1. Scrape leaguepedia
    scraping_result = scrape_deeplol_name(player_name)
    if scraping_result:
        player_name = scraping_result[0]
        player_status = scraping_result[1]

        validate_result = deeplol.validate_player_name(player_name, player_status)
        if validate_result:
            assign_after_success(validate_result, player)
            return

    # 2. Try to find by player name
    validate_result = deeplol.validate_player_name(player_name)
    if validate_result:
        assign_after_success(validate_result, player)
        return

    print(f"Failed to find deeplol profile for {player_name}")
    return

# Test usage
if __name__ == "__main__":
    test_player=Player(name="mikusik")
    find_deeplol_name(test_player)
    print(test_player.deeplol_name, test_player.deeplol_status)