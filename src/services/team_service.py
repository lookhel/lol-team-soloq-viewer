from models import Team
from clients.leaguepedia_api import LeaguepediaAPI


def check_team_subs(team: Team) -> None:
    """
    Checks who is probably sub based on latest roster (Leaguepedia API information in players table is not accurate)
    """
    team_overview = team.overview_page

    leaguepedia = LeaguepediaAPI()
    latest_roster = leaguepedia.fetch_latest_roster(team_overview)


    for player in team.players:
        if latest_roster:
            if {player.overview_page, player.name}.isdisjoint(latest_roster):
                player.is_substitute = True