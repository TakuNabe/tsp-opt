"""Contains the application service for location management."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

import polars as pl

from src.domain.model import Coordinate, LocationSchema
from src.domain.service.location import LocationDomainService

if TYPE_CHECKING:
    from src.infra._base import BaseStorageAdapter, BaseWritableRepository, PathLike


class LocationAppService:
    """Application service for location management operations."""

    def __init__(
        self, repository: BaseWritableRepository, storage_adapter: BaseStorageAdapter, data_uri: PathLike,
    ) -> None:
        """
        Args:
            repository (BaseWritableRepository): The location repository.
            storage_adapter (BaseStorageAdapter): The storage adapter for file I/O.
            data_uri (PathLike): The path to the persistent locations CSV file.
        """
        self._repository = repository
        self._storage_adapter = storage_adapter
        self._data_uri = data_uri

    def get_all_locations(self) -> pl.DataFrame:
        """Get all locations as a Polars DataFrame.

        Returns empty DataFrame with correct schema if the file does not exist.

        Returns:
            pl.DataFrame: The locations DataFrame.
        """
        try:
            return self._repository.read_as_polars()
        except FileNotFoundError:
            return pl.DataFrame(schema={
                "id": pl.Utf8,
                "name": pl.Utf8,
                "address": pl.Utf8,
                "latitude": pl.Float64,
                "longitude": pl.Float64,
            })

    def add_location(
        self, *, id_: str, name: str, address: str, latitude: float, longitude: float,
    ) -> pl.DataFrame:
        """Add a single location. Validates coordinates and checks for duplicate ID.

        Args: -----
            id_ (str): The location ID.
            name (str): The location name.
            address (str): The location address.
            latitude (float): The latitude coordinate.
            longitude (float): The longitude coordinate.

        Returns:
            pl.DataFrame: The updated locations DataFrame.

        Raises:
            ValidationError: If coordinates are invalid.
            ValueError: If the ID already exists.
        """
        Coordinate(latitude=latitude, longitude=longitude)

        current_df = self.get_all_locations()
        if LocationDomainService.check_duplicate_id(current_df, id_):
            msg = f"Location ID '{id_}' already exists"
            raise ValueError(msg)

        new_row = pl.DataFrame(
            {"id": [id_], "name": [name], "address": [address], "latitude": [latitude], "longitude": [longitude]},
        )
        updated_df = pl.concat([current_df, new_row])
        self._repository.save(updated_df)
        return updated_df

    def update_location(
        self, *, id_: str, name: str, address: str, latitude: float, longitude: float,
    ) -> pl.DataFrame:
        """Update an existing location by ID.

        Args: -----
            id_ (str): The location ID.
            name (str): The updated location name.
            address (str): The updated location address.
            latitude (float): The updated latitude coordinate.
            longitude (float): The updated longitude coordinate.

        Returns:
            pl.DataFrame: The updated locations DataFrame.

        Raises:
            ValidationError: If coordinates are invalid.
            ValueError: If the ID does not exist.
        """
        Coordinate(latitude=latitude, longitude=longitude)

        current_df = self.get_all_locations()
        if not LocationDomainService.check_duplicate_id(current_df, id_):
            msg = f"Location ID '{id_}' not found"
            raise ValueError(msg)

        filtered = current_df.filter(pl.col("id") != id_)
        new_row = pl.DataFrame(
            {"id": [id_], "name": [name], "address": [address], "latitude": [latitude], "longitude": [longitude]},
        )
        updated_df = pl.concat([filtered, new_row])
        self._repository.save(updated_df)
        return updated_df

    def delete_location(self, id_: str) -> pl.DataFrame:
        """Delete a location by ID.

        Args: -----
            id_ (str): The ID of the location to delete.

        Returns:
            pl.DataFrame: The resulting DataFrame after deletion.
        """
        return self._repository.delete_by_id(id_)

    def upload_file(self, file_bytes: bytes, file_name: str) -> pl.DataFrame:
        """Upload and validate a CSV or Parquet file.

        Args: -----
            file_bytes (bytes): The file content as bytes.
            file_name (str): The file name (used to detect format).

        Returns:
            pl.DataFrame: The validated DataFrame.

        Raises:
            ValueError: If the file format is unsupported.
            pandera.errors.SchemaError: If the data does not conform to LocationSchema.
        """
        if file_name.endswith(".csv"):
            uploaded_df = pl.read_csv(BytesIO(file_bytes))
        elif file_name.endswith(".parquet"):
            uploaded_df = pl.read_parquet(BytesIO(file_bytes))
        else:
            msg = f"Unsupported file format: {file_name}"
            raise ValueError(msg)

        return LocationSchema.validate(uploaded_df)

    def save_uploaded(self, df: pl.DataFrame) -> None:
        """Persist an uploaded DataFrame, replacing all existing data.

        Args: -----
            df (pl.DataFrame): The validated DataFrame to save.
        """
        self._repository.save(df)
