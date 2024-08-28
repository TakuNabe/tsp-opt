"""Contains the domain model (including entities and value objects) classes."""

from .coordinate import Coordinate, Distance
from .schema.location import LocationSchema

__all__ = ["Coordinate", "Distance", "LocationSchema"]
