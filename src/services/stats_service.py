from collections import defaultdict

def merge_summoner_stats(all_stats: list[list[dict]]) -> list[dict]:
    grouped = defaultdict(list)

    for summoner_stats in all_stats:
        for stat in summoner_stats:
            grouped[stat["champion_id"]].append(stat)

    def merge_group(stats_list: list[dict]) -> dict:
        total_games = sum(s["games"] for s in stats_list)
        total_wins = sum(s["wins"] for s in stats_list)
        total_losses = sum(s["losses"] for s in stats_list)

        if total_games == 0:
            return {}

        def wavg(key):
            return sum(s[key] * s["games"] for s in stats_list) / total_games

        kills = wavg("kills")
        assists = wavg("assists")
        deaths = wavg("deaths")

        merged_dict = {
            "champion_id": stats_list[0]["champion_id"],

            "games": total_games,
            "wins": total_wins,
            "losses": total_losses,
            "win_rate": (total_wins / total_games) * 100,

            "kills": kills,
            "assists": assists,
            "deaths": deaths,

            "kda": (
                (kills + assists) / deaths
                if deaths > 0 else (kills + assists)
            ),

            "damage_dealt_per_min": wavg("damage_dealt_per_min"),
            "damage_taken_per_min": wavg("damage_taken_per_min"),
            "cs_per_min": wavg("cs_per_min"),

            "gold_diff_15": wavg("gold_diff_15"),
            "cs_15": wavg("cs_15"),

            "gold_per_team": wavg("gold_per_team"),
            "damage_per_team": wavg("damage_per_team"),
        }

        return {
            k: round(v, 2) if isinstance(v, float) else v for k, v in merged_dict.items()
        }

    merged = [
        merge_group(stats)
        for stats in grouped.values()
    ]


    return merged
