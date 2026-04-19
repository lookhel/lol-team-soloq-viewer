import time
from sqlite3 import Connection

from src.models import Team, Player


def _upsert_team(conn: Connection, team: Team, now) -> int:

    conn.execute(
        """
        INSERT INTO teams (name, overview_page, short, org_location, region, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (overview_page) DO UPDATE SET 
            overview_page = excluded.overview_page,
            short         = excluded.short,
            org_location  = excluded.org_location,
            region        = excluded.region,
            last_updated  = excluded.last_updated
        """,
        (team.name, team.overview_page, team.short, team.org_location, team.region, now)
    )

    team_id = conn.execute(
        """
        SELECT id
        FROM teams
        WHERE overview_page = ?
        """,
        (team.overview_page,)
    ).fetchone()['id']

    return team_id

def _sync_players(conn: Connection, team_id: int, players: list[Player], now: int) -> None:
    current_players = {player.overview_page for player in players if player.overview_page is not None}

    existing_rows = conn.execute(
        """
        SELECT overview_page
        FROM players
        WHERE team_id = ?
        """,
        (team_id,)
    ).fetchall()

    existing_players = {row['overview_page'] for row in existing_rows}
    players_to_unassign = existing_players - current_players

    for player in players_to_unassign:
        conn.execute(
            """
            UPDATE players
            SET team_id       = NULL,
                is_substitute = NULL,
                last_updated  = ?
            WHERE overview_page = ?
            """,
            (now, player)
        )

    for player in players:
        conn.execute(
            """
            INSERT INTO players (overview_page, team_id, name, role, is_substitute, deeplol_name, deeplol_status,
                                 last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (overview_page) DO UPDATE SET 
                team_id        = excluded.team_id,
                name           = excluded.name,
                role           = excluded.role,
                is_substitute  = excluded.is_substitute,
                deeplol_name   = excluded.deeplol_name,
                deeplol_status = excluded.deeplol_status,
                last_updated   = excluded.last_updated
            """,
            (
                player.overview_page,
                team_id,
                player.name,
                player.role.value if player.role else None,
                1 if player.is_substitute else 0 if player.is_substitute is not None else None,
                player.deeplol_name,
                player.deeplol_status,
                now
            )
        )

def save_team(conn: Connection, team: Team) -> None:
    now = int(time.time())

    team_id = _upsert_team(conn, team, now)
    _sync_players(conn, team_id, team.players, now)