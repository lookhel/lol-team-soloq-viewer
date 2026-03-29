from clients import DeepLolAPI, Summoner

# Test players
players = [('Cinkrof', 'sad'), ('G2 Caps', '1323')]

def main():
    with DeepLolAPI() as deeplol:
        deeplol.fetch_current_season()

        summoners = [Summoner(player[0], player[1]) for player in players]
        for s in summoners:
            s.puu_id = deeplol.fetch_summoner_puu_id(s)
            s.champion_stats = deeplol.fetch_summoner_champion_stats(s)
            print(s)

if __name__ == "__main__":
    main()