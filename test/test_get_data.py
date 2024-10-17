from datetime import datetime
from unittest.mock import patch

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.data_pipeline.config import API_URL
from src.data_pipeline.get_data import (
    convert_date_string,
    fetch_data_from_api,
    update_or_create_item,
)
from src.data_pipeline.models import Base, User


def test_convert_date_string():
    """
    Test the convert_date_string function for various input formats.
    """
    date_string = "2023-03-16T01:11:27.466669"
    result = convert_date_string(date_string)
    assert isinstance(result, datetime)
    assert result == datetime(2023, 3, 16, 1, 11, 27, 466669)


@patch("src.data_pipeline.get_data.requests.get")
def test_fetch_data_from_api(mock_get):
    """
    Test the fetch_data_from_api function for both successful and error scenarios.

    This test uses mocking to:
    1. Simulate a successful API call and verify the correct handling of the response.
    2. Simulate an API error and ensure the function returns an empty list.
    """
    # simluate successful API call
    example_item = {
        "id": 12643,
        "name": "elevate",
        "artist": "Human Movement",
        "songwriters": "Jeffrey Hicks",
        "duration": "5:35",
        "genres": "energy",
        "album": "kinetic",
        "created_at": "2023-03-16T01:11:27.466669",
        "updated_at": "2024-08-08T10:15:17.621586",
    }
    mock_get.return_value.json.return_value = {"items": [example_item]}
    mock_get.return_value.raise_for_status.return_value = None

    result = fetch_data_from_api("test_endpoint")
    assert result == [example_item]
    mock_get.assert_called_once_with(f"{API_URL}/test_endpoint", timeout=10)

    # Error simulation
    mock_get.side_effect = requests.RequestException("API Error")
    result_error = fetch_data_from_api("test_endpoint")
    assert result_error == []


@pytest.fixture
def db_session():
    # Create memory session for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()


def test_update_or_create_item(db_session):
    """
    Test the update_or_create_item function for both creation and update scenarios.

    This test:
    1. Creates a new user and verifies it's added to the database correctly.
    2. Updates an existing user and verifies the changes are reflected in the database.
    """

    # Test to create a new item
    new_user_data = {
        "id": 1,
        "first_name": "test",
        "last_name": "user",
        "email": "test@example.com",
    }
    update_or_create_item(db_session, User, new_user_data)
    user = db_session.query(User).filter_by(id=1).first()
    assert user is not None
    assert user.first_name == "test"
    assert user.last_name == "user"
    assert user.email == "test@example.com"

    # Test to update an existing item
    updated_user_data = {
        "id": 1,
        "first_name": "updated",
        "email": "updated@example.com",
    }
    update_or_create_item(db_session, User, updated_user_data)
    updated_user = db_session.query(User).filter_by(id=1).first()
    assert updated_user.first_name == "updated"
    assert updated_user.email == "updated@example.com"
    assert updated_user.last_name == "user"
