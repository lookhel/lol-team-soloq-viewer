import time
from sqlite3 import Connection

from src.models import Team


def save_competition(conn: Connection, competition_name: str, teams: list[Team]) -> None:
    now = int(time.time())

    conn.execute(
        """INSERT INTO competitions(name, last_updated)
        VALUES(?, ?)
        ON CONFLICT (name) DO UPDATE SET last_updated = excluded.last_updated
        """,
        (competition_name, now)
    )

    competition_id = conn.execute(
        """
        SELECT id FROM competitions WHERE name = ?
        """,
        (competition_name,)
    ).fetchone()['id']

    conn.execute(
        """
        DELETE FROM competition_teams WHERE competition_id = ?
        """,
        (competition_id,)
    )

    for team in teams:

        team_id = conn.execute(
            """
            SELECT id
            FROM teams
            WHERE overview_page = ?
            """,
            (team.overview_page,)
        ).fetchone()['id']

        conn.execute(
            """
            INSERT OR IGNORE INTO competition_teams (competition_id, team_id) VALUES (?, ?)
            """,
            (competition_id, team_id)
        )