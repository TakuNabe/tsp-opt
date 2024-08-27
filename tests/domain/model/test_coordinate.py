"""Test cases for the Coordinate relatesd models."""

import pytest
from pydantic import ValidationError

from src.domain.model.coordinate import Coordinate, Distance


def test_coordinate_model() -> None:
    """Test the Coordinate model."""
    latitude = 10.0
    longitude = 20.0
    coordinate = Coordinate(latitude=latitude, longitude=longitude)
    assert coordinate.latitude == latitude  # noqa: S101
    assert coordinate.longitude == longitude  # noqa: S101


def test_coordinate_model_validation() -> None:
    """Test the Coordinate model validation."""
    latitude = 10.0
    longitude = 20.0
    coordinate = Coordinate(latitude=latitude, longitude=longitude)
    assert coordinate.latitude == latitude  # noqa: S101
    assert coordinate.longitude == longitude  # noqa: S101

    with pytest.raises(ValidationError):
        Coordinate(latitude=-100, longitude=20.0)

    with pytest.raises(ValidationError):
        Coordinate(latitude=10.0, longitude=200)


def test_distance_model() -> None:
    """Test the Distance model."""
    distance_value = 10.0
    distance = Distance(value=distance_value)
    assert distance.value == distance_value  # noqa: S101


def test_distance_model_validation() -> None:
    """Test the Distance model validation."""
    distance_value = 10.0
    distance = Distance(value=distance_value)
    assert distance.value == distance_value  # noqa: S101

    with pytest.raises(ValidationError):
        Distance(value=-10.0)


def test_calculate_distance_from_coordinates() -> None:
    """Test the calculate_distance_from_coordinates method."""
    coordinate1 = Coordinate(latitude=35.180, longitude=136.907)
    coordinate2 = Coordinate(latitude=35.689, longitude=139.692)
    distance = Distance.calculate_distance_from_coordinates(coordinate1, coordinate2)
    assert round(distance, 5) == 259104.94942  # noqa: PLR2004, S101
