import sqlite3
from pathlib import Path
from sqlite3 import Connection

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / 'data' / 'cache.db'
SCHEMA_PATH = BASE_DIR / 'src' / 'db' / 'sql'

def init_db() -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            schema_files = sorted(Path(SCHEMA_PATH).glob('*.sql'))

            for file in schema_files:
                sql_instruction = file.read_text(encoding='utf-8')
                cursor.executescript(sql_instruction)

            conn.commit()

    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)

def get_connection() -> Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

if __name__ == '__main__':
    example_teams = ['Esprit Shōnen', 'Galions', 'Ici Japon Corp. Esport', 'Joblife', 'Karmine Corp Blue', 'Skillcamp',
                     'Solary', 'TLN Pirates', 'Vitality.Bee', 'ZYB Esport']
    init_db()
    with get_connection() as conn:
        conn.commit()