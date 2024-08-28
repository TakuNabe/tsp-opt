"""Contains the Schema model of location data including coordinates."""

import pandera.polars as pa
import polars as pl

from src.domain.model.schema.mixin import DataFrameModelMixin


class LocationSchema(pa.DataFrameModel, DataFrameModelMixin):
    """Schema model for location data."""

    id: pl.Utf8 = pa.Field(title="Location ID", nullable=False, coerce=True, description="Unique location ID")
    name: pl.Utf8 = pa.Field(title="Location Name", nullable=False, coerce=True, description="Location name")
    address: pl.Utf8 = pa.Field(title="Location Address", nullable=False, coerce=True, description="Location address")
    latitude: pl.Float64 = pa.Field(title="Latitude", nullable=False, coerce=True, description="Latitude coordinate")
    longitude: pl.Float64 = pa.Field(title="Longitude", nullable=False, coerce=True, description="Longitude coordinate")
