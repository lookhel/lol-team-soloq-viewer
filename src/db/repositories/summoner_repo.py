import json
import time
from sqlite3 import Connection

from src.models import Player, Summoner


def save_player_summoners(conn: Connection, player: Player) -> None:
    if not player.overview_page:
        raise ValueError(f"Player {player.name} has no overview_page")

    now = int(time.time())

    player_row = conn.execute(
        """
        SELECT id
        FROM players
        WHERE overview_page = ?
        """,
        (player.overview_page,)
    ).fetchone()

    if player_row is None:
        raise ValueError(f"Player {player.overview_page} is not saved in database")

    player_id = player_row['id']

    current_puu_ids = {s.puu_id for s in player.summoners if s.puu_id is not None}

    existing_summoners = conn.execute(
        """
        SELECT puu_id
        FROM summoners
        WHERE player_id = ?
        """,
        (player_id,)
    ).fetchall()

    existing_puu_ids = {s['puu_id'] for s in existing_summoners if s['puu_id']}

    puu_ids_to_remove = existing_puu_ids - current_puu_ids

    for puu_id in puu_ids_to_remove:
        conn.execute(
            """
            DELETE
            FROM summoners
            WHERE puu_id = ?
            """,
            (puu_id,)
        )

    for summoner in player.summoners:
        if not summoner.puu_id:
            continue

        conn.execute(
            """
            INSERT INTO summoners (puu_id, player_id, riot_id_name, riot_id_tag_line, platform_id, last_updated)
            VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (puu_id) DO
            UPDATE SET
                player_id = excluded.player_id,
                riot_id_name = excluded.riot_id_name,
                riot_id_tag_line = excluded.riot_id_tag_line,
                platform_id = excluded.platform_id,
                last_updated = excluded.last_updated
            """,
            (
                summoner.puu_id,
                player_id,
                summoner.riot_id_name,
                summoner.riot_id_tag_line,
                summoner.platform_id,
                now
            )
        )


def save_summoner_stats(conn: Connection, summoner: Summoner) -> None:
    now = int(time.time())

    conn.execute(
        """
        INSERT INTO summoner_stats (puu_id, champion_stats, last_updated)
        VALUES (?, ?, ?) ON CONFLICT (puu_id) DO
        UPDATE SET champion_stats = excluded.champion_stats,
            last_updated = excluded.last_updated
        """,
        (summoner.puu_id, json.dumps(summoner.champion_stats), now)
    )


def load_player_summoners(conn: Connection, player: Player) -> None:
    rows = conn.execute(
        """
        SELECT s.puu_id, s.riot_id_name, s.riot_id_tag_line, s.platform_id
        FROM summoners s
        JOIN players p ON s.player_id = p.id
        WHERE p.overview_page = ?
        """,
        (player.overview_page,)
    ).fetchall()

    if rows is None:
        return

    summoners = []

    for row in rows:
        summoners.append(
            Summoner(puu_id=row['puu_id'], riot_id_name=row['riot_id_name'], riot_id_tag_line=row['riot_id_tag_line'],
                     platform_id=row['platform_id'])
        )

    player.summoners = summoners

def load_summoner_stats(conn: Connection, summoner: Summoner) -> None:
    row = conn.execute(
        """
        SELECT champion_stats
        FROM summoner_stats
        WHERE puu_id = ?
        """,
        (summoner.puu_id,)
    ).fetchone()

    if row is None:
        return

    summoner.champion_stats = json.loads(row['champion_stats'])