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

competition_names = ['Rift Legends 2026 Spring', 'LPL 2026 Split 2', 'LCS 2026 Spring', 'LFL 2026 Spring',
                     'TCL 2026 Spring', 'LCK 2026 Rounds 1-2', 'LEC 2026 Spring']


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
                print(f"--------------------{team}")
                for player in team.players:
                    print(player)
                    if player.deeplol_name is None:
                         find_deeplol_name(player)
                    try:
                        check_if_sub(player)
                        deeplol.fetch_summoners_for_player(player)
                    except Exception as e:
                        print(e)
                        continue
                    save_player_summoners(conn, player)
                    for summ in player.summoners:
                        deeplol.fetch_summoner_champion_stats(summ)
                    save_summoner_stats(conn, summ)
                save_team(conn, team)


if __name__ == "__main__":
    main()
