"""Contains th repository classes for locations data."""

import pandera as pa
import polars as pl
from pandera.typing import DataFrame

from src.domain.model import LocationSchema
from src.infra._base import BaseRepository, BaseStorageAdapter, PathLike


class StorageLocationRepository(BaseRepository):
    """Repository for locations data using a storage adapter."""

    def __init__(self, storage_adapter: BaseStorageAdapter, uri: PathLike) -> None:
        """
        Args:
            storage_adapter (BaseStorageAdapter, optional): The storage adapter. Defaults to LocalStorageAdapter().
            uri (PathLike): The URI to the locations data.
        """
        self._storage_adapter = storage_adapter
        self._uri = uri

    @pa.check_types
    def read_as_polars(self) -> DataFrame[LocationSchema]:
        """
        Read the all rows of the locations data as a Polars DataFrame.

        Returns:
            DataFrame[LocationSchema]: The locations data as a Polars DataFrame.
        """
        return self._storage_adapter.read_csv_as_polars(self._uri, schema=LocationSchema.get_dtypes())

    def get_by_id(self, id_: str) -> list[dict]:
        """
        Get location records which match the ID.

        Args:
            id_ (str): The ID to match.

        Returns:
            list[dict]: Location records which match the ID.
        """
        return self.read_as_polars().filter(pl.col(LocationSchema.id) == id_).to_dicts()

    def get_by_name(self, name: str) -> list[dict]:
        """
        Get location records which match the name.

        Args:
            name (str): The name to match.

        Returns:
            list[dict]: Location records which match the name.
        """
        return self.read_as_polars().filter(pl.col(LocationSchema.name) == name).to_dicts()
