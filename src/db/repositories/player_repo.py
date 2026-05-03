import time
from sqlite3 import Connection
from typing import Literal

from src.models import Player

now = int(time.time())


def update_deeplol_profile(conn: Connection, player: Player, deeplol_name: str,
                           deeplol_status: Literal["pro", "streamer"]) -> None:
    if not player.overview_page:
        raise ValueError(f"Player {player.name} has not overview_page")

    cursor = conn.execute(
        """
        UPDATE players
        SET deeplol_name   = ?,
            deeplol_status = ?,
            last_updated   = ?
        WHERE overview_page = ?
        """,
        (deeplol_name, deeplol_status, now)
    )

    if cursor.rowcount == 0:
        raise ValueError(f"Player with overview_page {player.overview_page} not found in database")


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