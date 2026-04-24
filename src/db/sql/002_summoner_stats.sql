CREATE TABLE IF NOT EXISTS summoner_stats
(
    puu_id         TEXT PRIMARY KEY,
    champion_stats TEXT NOT NULL,
    last_updated   INT  NOT NULL,
    FOREIGN KEY (puu_id) REFERENCES summoners(puu_id)
)