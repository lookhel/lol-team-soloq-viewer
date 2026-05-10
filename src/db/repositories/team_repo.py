import time
from sqlite3 import Connection

from src.models import Team, Player


def _upsert_team(conn: Connection, team: Team, now) -> int:
    conn.execute(
        """
        INSERT INTO teams (name, overview_page, short, org_location, region, last_updated)
        VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT (overview_page) DO
        UPDATE SET name = excluded.name,
            overview_page = excluded.overview_page,
            short = excluded.short,
            org_location = excluded.org_location,
            region = excluded.region,
            last_updated = excluded.last_updated
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


def _sync_players(conn: Connection, team_id: int, players: list[Player]) -> None:
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
                is_substitute = NULL
            WHERE overview_page = ?
            """,
            (player,)
        )

    for player in players:
        conn.execute(
            """
            INSERT INTO players (overview_page, team_id, name, role, is_substitute, deeplol_name, deeplol_status)
            VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (overview_page) DO
            UPDATE SET team_id = excluded.team_id,
                name = excluded.name,
                role = excluded.role,
                is_substitute = excluded.is_substitute,
                deeplol_name = COALESCE (deeplol_name, excluded.deeplol_name),
                deeplol_status= COALESCE (deeplol_status, excluded.deeplol_status)
            """,
            (
                player.overview_page,
                team_id,
                player.name,
                player.role.value if player.role else None,
                1 if player.is_substitute else 0 if player.is_substitute is not None else None,
                player.deeplol_name,
                player.deeplol_status
            )
        )


def save_team_with_roster(conn: Connection, team: Team) -> None:
    if team is None:
        raise ValueError(f"team is None")

    now = int(time.time())

    team_id = _upsert_team(conn, team, now)
    _sync_players(conn, team_id, team.players)


def load_team(conn: Connection, team_overview) -> Team | None:
    team_row = conn.execute(
        """
        SELECT id, name, overview_page, short, org_location, region
        FROM teams
        WHERE overview_page = ? LIMIT 1
        """,
        (team_overview,)
    ).fetchone()

    if team_row is None:
        return None

    team = Team(
        name=team_row['name'],
        overview_page=team_row['overview_page'],
        short=team_row['short'],
        org_location=team_row['org_location'],
        region=team_row['region'],
    )

    player_rows = conn.execute(
        """
        SELECT name, overview_page, role, is_substitute, deeplol_name, deeplol_status
        FROM players
        WHERE team_id = ?
        ORDER BY CASE role
                     WHEN 'Top' THEN 1
                     WHEN 'Jungle' THEN 2
                     WHEN 'Mid' THEN 3
                     WHEN 'Bot' THEN 4
                     WHEN 'Support' THEN 5
                     ELSE 99
                     END,
                 name
        """,
        (team_row['id'],)
    ).fetchall()

    for row in player_rows:
        player = Player(
            name=row['name'],
            overview_page=row['overview_page'],
            role=row['role'],
            is_substitute=bool(row['is_substitute']),
        )
        player.deeplol_name = row['deeplol_name']
        player.deeplol_status = row['deeplol_status']

        team.assign_player(player)

    return team
