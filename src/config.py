import logging
import tomllib
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {
    "jobs_intervals": [
        "champions_hours",
        "competitions_hours",
        "deeplol_names_minutes",
        "summoners_for_players_minutes",
        "summoners_stats_minutes",
    ],
    "requests_per_job_limit": [
        "deeplol_names",
        "summoners_for_players",
        "summoners_stats",
    ],
    "stored_data_max_age": [
        "deeplol_names_days",
        "summoners_for_players_hours",
        "summoners_stats_hours",
    ],
}

def _validate_config(config: dict) -> None:
    """
    Checks if all required keys are present in the config file.
    """
    missing = []

    for section, keys in REQUIRED_KEYS.items():
        if section not in config:
            missing.append(section)
            continue

        for key in keys:
            if key not in config[section]:
                missing.append(f"{section}.{key}")

    if missing:
        raise KeyError(f"Missing config keys: {', '.join(missing)}")


@lru_cache(maxsize=1)
def load_config(config_path: Path) -> dict:
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        logger.critical("Config file not found: %s", config_path)
        raise
    except tomllib.TOMLDecodeError as e:
        logger.critical("Invalid TOML in config: %s", e)
        raise

    _validate_config(config)

    logger.info("Config loaded and validated successfully")
    return config

def load_competition_names(competitions_path: Path) -> dict:
    try:
        with open(competitions_path, "rb") as f:
            competitions = tomllib.load(f)
    except FileNotFoundError:
        logger.critical("Competitions file not found: %s", competitions_path)
        raise
    except tomllib.TOMLDecodeError as e:
        logger.critical("Invalid TOML in competitions: %s", e)
        raise

    logger.info("Competition names loaded successfully")
    return competitions