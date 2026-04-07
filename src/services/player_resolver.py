from src.clients.leaguepedia_scrape import scrape_deeplol_name
from src.clients.deeplol import DeepLolAPI
from src.models import Player

def find_deeplol_name(player: Player):

    player_name = player.name

    # 1. Scrape leaguepedia
    scrape_deeplol_name(player_name)