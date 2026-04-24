from src.clients.leagupedia_api import LeaguepediaAPI
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
from src.services.player_service import find_deeplol_name, check_if_sub

example_teams = ['Esprit Shōnen', 'Galions', 'Ici Japon Corp. Esport', 'Joblife', 'Karmine Corp Blue', 'Skillcamp',
                 'Solary', 'TLN Pirates', 'Vitality.Bee', 'ZYB Esport']
competition_names = ['Rift Legends 2026 Spring', 'LPL 2026 Split 2', 'LCS 2026 Spring', 'LFL 2026 Spring']


def main():
    init_db()
    with get_connection() as conn:
        print(load_competition_names(conn))
        team = load_team(conn, 'Barcząca Esports')
        for player in team.players:
            load_player_summoners(conn, player)
            with DeepLolAPI() as deeplol:
                for summoner in player.summoners:
                    print(summoner)
                    print(summoner.champion_stats)
                    load_summoner_stats(conn, summoner)
                    print(summoner.champion_stats)
        print(load_competition_teams(conn, 'Rift Legends 2026 Spring'))
    exit()

    leaguepedia = LeaguepediaAPI()
    all_teams = []

    with get_connection() as conn:

        for competition in competition_names:
            print(competition)
            competition_teams = leaguepedia.fetch_competition_teams(competition)
            all_teams.extend(competition_teams)
            leaguepedia.fetch_teams_rosters(competition_teams)
            for team in competition_teams:
                save_team(conn, team)
            save_competition(conn, competition, competition_teams)
            print(competition_teams)

        with DeepLolAPI() as deeplol:
            for team in all_teams:
                for player in team.players:
                    print(player)
                    find_deeplol_name(player)
                    check_if_sub(player)
                    try:
                        deeplol.fetch_summoners_for_player(player)
                    except Exception as e:
                        print(e)
                        continue
                    save_player_summoners(conn, player)
                save_team(conn, team)


if __name__ == "__main__":
    main()
