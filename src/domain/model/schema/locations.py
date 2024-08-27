"""Contains the Schema model of location data including coordinates."""

import pandera as pa
from pandera.typing import Series


class LocationSchema(pa.SchemaModel):
    """Schema model for location data."""

    id: Series[str] = pa.Field(title="Location ID", nullable=False, coerce=True, description="Unique location ID")
    name: Series[str] = pa.Field(title="Location Name", nullable=False, coerce=True, description="Location name")
    address: Series[str] = pa.Field(
        title="Location Address", nullable=False, coerce=True, description="Location address"
    )
    latitude: Series[float] = pa.Field(title="Latitude", nullable=False, coerce=True, description="Latitude coordinate")
    longitude: Series[float] = pa.Field(
        title="Longitude", nullable=False, coerce=True, description="Longitude coordinate"
    )
