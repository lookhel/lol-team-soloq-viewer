import json
import time

from src.clients import DeepLolAPI, LeaguepediaAPI
from src.models import Player, Team, Role

# Test teams
#team_names = ['Forsaken (Polish Team)', 'Bomba Team', 'Barcząca Esports']

competition_name = 'Rift Legends 2026 Spring'

def main():
    leaguepedia=LeaguepediaAPI()

    with open('./data/rl.json', 'w', encoding='utf-8') as f:
        teams = leaguepedia.fetch_competition_teams(competition_name)
        competition_teams = {'competition': competition_name, 'teams': teams, 'last_updated': time.time()}
        json.dump(competition_teams, f, indent=4, ensure_ascii=False)

    if teams:
        teams = leaguepedia.fetch_teams(teams)
        leaguepedia.fetch_teams_rosters(teams)

    for t in teams:
        print(t)
        print(t.players)

    with DeepLolAPI() as deeplol:
        for team in teams:
            print(team)
            for p in team.players:
                deeplol.fetch_summoners_for_player(p)
                print(p)
                for s in p.summoners:
                    deeplol.fetch_summoner_champion_stats(s)
                    print(s)
                    print(s.champion_stats)

if __name__ == "__main__":
    main()