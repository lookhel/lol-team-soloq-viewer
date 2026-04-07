g2 = Team('G2 Esports', 'G2')  # Fetch team

g2_players = ["BrokenBlade", "Skewmond", "Caps", "Hans Sama", "Labrov"]  # Fetch players
g2_players = [Player(p) for p in g2_players]

roles = list(Role)
for player, role in zip(g2_players, roles):
    g2.assign_player(player, role)

g2_summoners = {
    "BrokenBlade": Summoner('G2 Brokenblade', '1918'),
    "Skewmond": Summoner('G2 Skewmond', '3327'),
    "Caps": Summoner('G2 Caps', '1323'),
    "Hans Sama": Summoner('G2 Hans Sama', '12838'),
    "Labrov:": Summoner('G2 Labrov', '8085')
}

for player, summoner in zip(g2_players, g2_summoners.values()):
    player.assign_summoner(summoner)
    print(player.summoners)

with DeepLolAPI() as deeplol:
    for player in g2_players:
        for summoner in player.summoners:
            deeplol.fetch_summoner_champion_stats(summoner)
            print(player, summoner, summoner.champion_stats)
            if not saved:
                with open("filtered.json", "w") as f:
                    json.dump(summoner.champion_stats, f, indent=4)
                saved = True