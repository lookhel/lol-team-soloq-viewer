# LoL Team SoloQ Viewer

## Overview

Backend application for collecting and serving League of Legends SoloQ statistics for entire team rosters in one place.

### Live API
Base URL: <https://lol.lookhel.dev/api>

Swagger docs: <https://lol.lookhel.dev/api/docs>

### Tech stack
- **FastAPI** - REST API
- **APScheduler** - scheduled regular data collection
- **SQLite** - local data storage
- **Docker and Docker Compose** - containerized deployment

### Data sources
- Leaguepedia - team rosters and players other platforms profiles
- Deeplol - summoner profiles and SoloQ statistics (Unofficial API)
- DDragon - static game data (champions)

## Getting started

### Prerequisites
- Docker
- Docker Compose

### Running the application

Clone repo.
```bash
git clone https://github.com/lookhel/lol-team-soloq-viewer.git
cd lol-team-soloq-viewer
```

Copy `.env.example` to `.env` and insert bot credentials from Gamepedia created here [Fandom Bot Passwords](https://help.fandom.com/wiki/Special:BotPasswords).
You can also specify an `API_ROOT_PATH` if running the application behind a reverse proxy with a path prefix.
```env
# Leaguepedia username (without "@bot_name" )
LEAGUEPEDIA_USERNAME=

# Bot password
# Required format: @<bot_name><password>
LEAGUEPEDIA_BOT_PASSWORD=

# Base path when running behind reverse proxy (e.g. /api)
API_ROOT_PATH=
```

Create `competitions.toml` to specify which competitions will be supported. Competition names should match **Event** field from [Current Leagues](https://lol.fandom.com/wiki/Special:CargoTables/CurrentLeagues) on Leaguepedia.
```toml
# competitions.toml
names = [
    "Rift Legends 2026 Spring",
    "LEC 2026 Spring Playoffs",
    "LPL 2026 Split 2"
]
```

Run app with docker compose.
```bash
docker compose up --build
```
API will be available at <http://127.0.0.1:8001>.

> **Note**:
> The database is initially empty. After startup, the background scheduler gradually fetches and saves data for configured competitions.
> Depending on the number of tracked competitions and scheduler intervals, full data synchronization may take several hours.