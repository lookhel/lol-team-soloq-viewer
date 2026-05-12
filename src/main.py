import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

import uvicorn
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from src.api.routes import router
from src.config import load_config, load_competition_names
from src.db.database import init_db
from src.services.update import (
    refresh_competitions_data,
    refresh_deeplol_names,
    refresh_summoners_for_players,
    refresh_summoners_stats,
    refresh_champions,
)

CONFIG_FILE = Path(__file__).parents[1] / "config.toml"
COMPETITIONS_FILE = Path(__file__).parents[1] / "competitions.toml"

ROOT_PATH = os.getenv("API_ROOT_PATH")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

config = load_config(CONFIG_FILE)
competitions = load_competition_names(COMPETITIONS_FILE)

scheduler = BackgroundScheduler(
    job_defaults={
        'max_instances': 1,
        'coalesce': True,
        'misfire_grace_time': 300
    },
    executors={
        'default': ThreadPoolExecutor(max_workers=1),
    }
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application")

    init_db()

    scheduler.add_job(refresh_champions, 'interval', hours=config['jobs_intervals']['champions_hours'],
                      next_run_time=datetime.now() + timedelta(seconds=10))
    scheduler.add_job(refresh_competitions_data, 'interval', hours=config['jobs_intervals']['competitions_hours'],
                      kwargs={'competitions': competitions['names']},
                      next_run_time=datetime.now() + timedelta(seconds=20))
    scheduler.add_job(refresh_deeplol_names, 'interval', minutes=config['jobs_intervals']['deeplol_names_minutes'],
                      kwargs={'limit': config['requests_per_job_limit']['deeplol_names'],
                              'max_age_days': config['stored_data_max_age']['deeplol_names_days']})
    scheduler.add_job(refresh_summoners_for_players, 'interval',
                      minutes=config['jobs_intervals']['summoners_for_players_minutes'],
                      kwargs={'limit': config['requests_per_job_limit']['summoners_for_players'],
                              'max_age_hours': config['stored_data_max_age']['summoners_for_players_hours']})
    scheduler.add_job(refresh_summoners_stats, 'interval', minutes=config['jobs_intervals']['summoners_stats_minutes'],
                      kwargs={'limit': config['requests_per_job_limit']['summoners_stats'],
                              'max_age_hours': config['stored_data_max_age']['summoners_stats_hours']})

    scheduler.start()

    yield

    logger.info("Shutting down the application")
    scheduler.shutdown()


app = FastAPI(title="LoL Team SoloQ Viewer API", lifespan=lifespan, root_path=ROOT_PATH or None)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
