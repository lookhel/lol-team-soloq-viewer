import time
from sqlite3 import Connection

from src.models import Team


def save_competition(conn: Connection, competition_name: str, teams: list[Team]) -> None:
    now = int(time.time())

    conn.execute(
        """INSERT INTO competitions(name, last_updated)
           VALUES (?, ?)
           ON CONFLICT (name) DO UPDATE SET last_updated = excluded.last_updated
        """,
        (competition_name, now)
    )

    competition_id = conn.execute(
        """
        SELECT id
        FROM competitions
        WHERE name = ?
        """,
        (competition_name,)
    ).fetchone()['id']

    conn.execute(
        """
        DELETE
        FROM competition_teams
        WHERE competition_id = ?
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
            INSERT OR IGNORE INTO competition_teams (competition_id, team_id)
            VALUES (?, ?)
            """,
            (competition_id, team_id)
        )

def load_competition_names(conn: Connection) -> list[str]:
    competitions = conn.execute(
        """
        SELECT name FROM competitions
        """
    ).fetchall()

    competition_names = [competition['name'] for competition in competitions]

    return competition_names

def load_competition_teams(conn: Connection, competition_name) -> list[Team]:
    team_rows = conn.execute(
        """
        SELECT t.name, t.overview_page, t.short, t.org_location, t.region
        FROM teams t
        JOIN competition_teams ct ON ct.team_id = t.id
        JOIN competitions c ON ct.competition_id = c.id
        WHERE c.name = ?
        """,
        (competition_name,)
    )

    teams = [Team(name=row['name'], overview_page=row['overview_page'],
                  short=row['short'], org_location=row['org_location'],
                  region=row['region']) for row in team_rows]

    return teams