CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    last_updated INTEGER NOT NULL
    );

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name TEXT,
    overview_page TEXT NOT NULL UNIQUE,
    short TEXT,
    org_location TEXT,
    region TEXT,
    last_updated INTEGER NOT NULL
    );

CREATE TABLE IF NOT EXISTS competition_teams (
    competition_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    PRIMARY KEY (competition_id, team_id),
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
    );

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    overview_page TEXT NOT NULL UNIQUE,
    team_id INTEGER,
    role TEXT,
    is_substitute INTEGER,
    deeplol_name TEXT,
    deeplol_status TEXT,
    last_updated INTEGER NOT NULL,
    UNIQUE(team_id, name),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS summoners (
    puu_id TEXT PRIMARY KEY,
    player_id INTEGER NOT NULL,
    riot_id_name TEXT NOT NULL,
    riot_id_tag_line TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    last_updated INTEGER NOT NULL,
    UNIQUE(player_id, riot_id_name, riot_id_tag_line, platform_id),
    FOREIGN KEY (player_id) REFERENCES players(id)
);





