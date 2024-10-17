import time
from datetime import datetime, timedelta
from typing import List, Type

import requests
import schedule
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import API_URL, SessionLocal, logger
from .models import Base, ListenHistory, Track, User


def get_db():
    """Manage database session connexion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def convert_date_string(date_string: str) -> datetime:
    """Convert date string to datetime."""
    if isinstance(date_string, str):
        return datetime.fromisoformat(date_string.rstrip("Z"))
    return date_string


def fetch_data_from_api(endpoint: str) -> List[dict]:
    """Get data from API for a given endpoint."""
    url = f"{API_URL}/{endpoint}"
    try:
        response = requests.get(url, timeout=10)  # Ajout d'un timeout
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.RequestException as e:
        logger.exception(f"API request error for {endpoint}: {str(e)}")
        return []


def update_or_create_item(session: Session, model: Type[Base], item: dict):
    """Update or create item in database."""
    existing_item = session.get(model, item["id"])
    if existing_item:
        for key, value in item.items():
            setattr(existing_item, key, value)
    else:
        new_item = model(**item)
        session.add(new_item)


def process_data(model: Type[Base], items: List[dict]):
    """Treat data for a given model."""
    with next(get_db()) as session:
        try:
            for item in items:
                item["created_at"] = convert_date_string(
                    item.get("created_at")
                )
                item["updated_at"] = convert_date_string(
                    item.get("updated_at")
                )
                update_or_create_item(session, model, item)
            session.commit()
            logger.info(
                f"{len(items)} {model.__name__} records processed successfully"
            )
        except SQLAlchemyError as e:
            session.rollback()
            logger.exception(
                f"Database error while processing {model.__name__}: {str(e)}"
            )


def fetch_and_process_data(endpoint: str, model: Type[Base]):
    """Fetch and process data for a given endpoint and data model."""
    items = fetch_data_from_api(endpoint)
    if items:
        process_data(model, items)


def process_listen_history(items: List[dict]):
    """Process listen history."""
    with next(get_db()) as session:
        try:
            for item in items:
                user = session.get(User, item["user_id"])
                if not user:
                    logger.warning(
                        f"User with id {item['user_id']} not found. Skipping this listen history."
                    )
                    continue

                listen_history = ListenHistory(
                    user=user,
                    created_at=convert_date_string(item.get("created_at")),
                    updated_at=convert_date_string(item.get("updated_at")),
                )

                for track_id in item["items"]:
                    track = session.get(Track, track_id)
                    if track:
                        listen_history.tracks.append(track)
                    else:
                        logger.warning(f"Track with id {track_id} not found.")

                session.add(listen_history)

            session.commit()
            logger.info(
                f"{len(items)} ListenHistory records processed successfully"
            )
        except SQLAlchemyError as e:
            session.rollback()
            logger.exception(
                f"Database error while processing ListenHistory: {str(e)}"
            )


def fetch_all_data():
    """Fetch and process data from the three API routes."""
    logger.info("Beginning of daily task to collect data from API")
    fetch_and_process_data("users", User)
    fetch_and_process_data("tracks", Track)

    listen_history_items = fetch_data_from_api("listen_history")
    if listen_history_items:
        process_listen_history(listen_history_items)

    logger.info("End of task")


def main():
    # start task scheduled 1 min after script launch
    now = datetime.now()
    next_run = now + timedelta(minutes=1)
    schedule_time = next_run.strftime("%H:%M")
    schedule.every().day.at(schedule_time).do(fetch_all_data)
    logger.info("Scheduler begins")

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logger.exception(f"An error occurred in the main loop: {str(e)}")
