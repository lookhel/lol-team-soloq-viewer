import time
from sqlite3 import Connection
from typing import Literal

from src.models import Player

def update_deeplol_profile(conn: Connection, player: Player) -> None:
    if not player.overview_page:
        raise ValueError(f"Player {player.name} has not overview_page")

    now = int(time.time())

    cursor = conn.execute(
        """
        UPDATE players
        SET deeplol_name   = ?,
            deeplol_status = ?,
            deeplol_checked_at = ?
        WHERE overview_page = ?
        """,
        (player.deeplol_name, player.deeplol_status, now, player.overview_page)
    )

    if cursor.rowcount == 0:
        raise ValueError(f"Player with overview_page {player.overview_page} not found in database")

def mark_deeplol_checked(conn: Connection, player: Player) -> None:
    if not player.overview_page:
        raise ValueError(f"Player {player.name} has no overview_page")

    now = int(time.time())

    cursor = conn.execute(
        """
        UPDATE players
        SET deeplol_checked_at = ?
        WHERE overview_page = ?
        """,
        (
            now,
            player.overview_page
        )
    )

    if cursor.rowcount == 0:
        raise ValueError(
            f"Player with overview_page {player.overview_page} not found in database"
        )


def load_deeplol_profile(conn: Connection, player: Player) -> None:
    row = conn.execute(
        """
        SELECT deeplol_name, deeplol_status
        FROM players
        WHERE overview_page = ?
        """,
        (player.overview_page,)
    ).fetchone()

    player.deeplol_name = row['deeplol_name']
    player.deeplol_status = row['deeplol_status']


def load_player(conn: Connection, player_overview: str) -> Player | None:
    row = conn.execute(
        """
        SELECT overview_page, name, role, is_substitute
        FROM players
        WHERE overview_page = ?
        """,
        (player_overview,)
    ).fetchone()

    if row is None:
        return None

    return Player(overview_page=row['overview_page'], name=row['name'],
                    role=row['role'], is_substitute=row['is_substitute'])


def get_players_needing_deeplol_check(conn, limit: int = 20, max_age_days: int = 7) -> list[Player]:

    threshold_timestamp = int(time.time()) - (max_age_days * 24 * 60 * 60)

    rows = conn.execute(
        """
        SELECT overview_page, name, is_substitute, deeplol_name, deeplol_status, deeplol_checked_at
        FROM players
        WHERE deeplol_name IS NULL
          AND (deeplol_checked_at IS NULL OR deeplol_checked_at < ?)
        ORDER BY deeplol_checked_at NULLS FIRST
        LIMIT ?
        """,
        (threshold_timestamp, limit)
    ).fetchall()

    players = []
    for row in rows:
        p = Player(
            name=row["name"],
            overview_page=row["overview_page"],
            is_substitute=bool(row["is_substitute"]) if row["is_substitute"] is not None else None
        )
        p.deeplol_name = row["deeplol_name"]
        p.deeplol_status = row["deeplol_status"]
        p.deeplol_checked_at = row["deeplol_checked_at"]
        players.append(p)

    return players

def get_players_needing_summoners_update(conn: Connection, limit=100, max_age_hours: int = 24) -> list[Player]:

    threshold = int(time.time()) - (max_age_hours * 3600)

    rows = (conn.execute(
        """
        SELECT name, overview_page, deeplol_name, deeplol_status
        FROM players
        WHERE deeplol_name IS NOT NULL AND (summoners_checked_at IS NULL OR summoners_checked_at < ?)
        ORDER BY summoners_checked_at NULLS FIRST
        LIMIT ?
        """,
        (threshold, limit)
    ).fetchall())

    players = []
    for row in rows:
        player = Player(
            name=row["name"],
            overview_page=row["overview_page"],
        )
        player.deeplol_name = row["deeplol_name"]
        player.deeplol_status = row["deeplol_status"]
        players.append(player)

    return players

def mark_summoners_checked(conn: Connection, player: Player) -> None:
    now = int(time.time())

    conn.execute(
        """
        UPDATE players
        SET summoners_checked_at = ?
        WHERE overview_page = ?
        """,
        (now, player.overview_page)
    )