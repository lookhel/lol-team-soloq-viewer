import logging
from sqlite3 import Connection

logger = logging.getLogger(__name__)

def save_champions(conn: Connection, champions: list[dict]) -> None:
    if not champions:
        logger.warning("No champions provided to save_champions")
        return

    conn.executemany(
        """
        INSERT INTO champions (id, name, image, version)
        VALUES (:id, :name, :image, :version)
        ON CONFLICT (id) DO UPDATE SET
            name = excluded.name,
            image = excluded.image,
            version = excluded.version
        """,
        champions
    )

def load_champions(conn: Connection) -> list[dict]:

    rows = conn.execute(
        """
        SELECT id, name, image, version
        FROM champions
        """
    ).fetchall()

    return [
    {
        "id": row['id'],
        "name": row['name'],
        "image": row['image'],
        "version": row['version']
    }
        for row in rows
    ]

def get_stored_ddragon_version(conn: Connection) -> str:
    row = conn.execute(
        """
        SELECT version
        FROM champions
        LIMIT 1
        """
    ).fetchone()

    return row['version'] if row else None