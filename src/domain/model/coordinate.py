"""Contains Domain model of coordinate related data.

- Coordinate: Contains the Coordinate model.
- Distance: Contains the Distance model.
"""

from geopy.distance import geodesic
from pydantic import BaseModel, field_validator


class Coordinate(BaseModel):
    """Coordinate model."""

    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def _validate_latitude(cls, v: float) -> float:
        min_latitude = -90
        max_latitude = 90
        if not min_latitude <= v <= max_latitude:
            error_message = "latitude must be in the range [-90, 90]"
            raise ValueError(error_message)
        return v

    @field_validator("longitude")
    @classmethod
    def _validate_longitude(cls, v: float) -> float:
        min_longitude = -180
        max_longitude = 180
        if not min_longitude <= v <= max_longitude:
            error_message = "longitude must be in the range [-180, 180]"
            raise ValueError(error_message)
        return v


class Distance(BaseModel):
    """Distance model. Note that the unit is meters."""

    value: float

    @field_validator("value")
    @classmethod
    def _validate_value(cls, v: float) -> float:
        if v < 0:
            error_message = "distance value must be greater than or equal to 0"
            raise ValueError(error_message)
        return v

    @classmethod
    def calculate_distance_from_coordinates(cls, coordinate1: Coordinate, coordinate2: Coordinate) -> float:
        """Calculate the distance between two coordinates in meters.

        Args:  # ------
            coordinate1 (Coordinate): The first coordinate.
            coordinate2 (Coordinate): The second coordinate.

        Returns:  # ------
            float: The distance between the two coordinates in meters.
        """
        return geodesic(
            (coordinate1.latitude, coordinate1.longitude), (coordinate2.latitude, coordinate2.longitude)
        ).meters
