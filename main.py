from db.repositories.competition_repo import save_competition
from db.repositories.summoner_repo import save_player_summoners
from src.clients.leagupedia_api import LeaguepediaAPI
from src.clients.deeplol import DeepLolAPI
from src.db.database import init_db, get_connection
from src.db.repositories.team_repo import save_team
from src.services.player_resolver import find_deeplol_name
from src.models import Team

example_teams = ['Esprit Shōnen', 'Galions', 'Ici Japon Corp. Esport', 'Joblife', 'Karmine Corp Blue', 'Skillcamp', 'Solary', 'TLN Pirates', 'Vitality.Bee', 'ZYB Esport']
competition_name = 'Rift Legends 2026 Spring'


def main():

    init_db()
    leaguepedia = LeaguepediaAPI()
    competitions = leaguepedia.fetch_current_competitions()

    teams = leaguepedia.fetch_competition_teams(competition_name)
    leaguepedia.fetch_teams_rosters(teams)
    print("teamsv1", teams)

    with DeepLolAPI() as deeplol:
        with get_connection() as conn:
            for team in teams:
                save_team(conn, team)
                for player in team.players:
                    print(player)
                    find_deeplol_name(player)
                    try:
                        deeplol.fetch_summoners_for_player(player)
                    except Exception as e:
                        print(e)
                        continue
                    save_player_summoners(conn, player)
                save_team(conn, team)
            save_competition(conn, competition_name, teams)

            conn.commit()

if __name__ == "__main__":
    main()