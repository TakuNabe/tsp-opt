"""Contains the base infrastructure classes."""

from abc import ABC, abstractmethod
from typing import TypeVar

import polars as pl

PathLike = TypeVar("PathLike", str, bytes)


class BaseStorageAdapter(ABC):
    """Base class for storage adapters."""

    @abstractmethod
    def read_csv_as_polars(self, path: str) -> pl.DataFrame:
        """Read a CSV file as a Polars DataFrame.

        Args: -----
            path (str): The path to the CSV file.

        Returns:
            pl.DataFrame: The Polars DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def read_parquet_as_polars(self, path: str) -> pl.DataFrame:
        """Read a Parquet file as a Polars DataFrame.

        Args: -----
            path (str): The path to the Parquet file.

        Returns:
            pl.DataFrame: The Polars DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def write_polars_as_csv(self, df: pl.DataFrame, path: PathLike) -> None:
        """Write a Polars DataFrame as a CSV file.

        Args: -----
            df (pl.DataFrame): The Polars DataFrame.
            path (PathLike): The path to the CSV file.
        """
        raise NotImplementedError

    @abstractmethod
    def write_polars_as_parquet(self, df: pl.DataFrame, path: PathLike) -> None:
        """Write a Polars DataFrame as a Parquet file.

        Args: -----
            df (pl.DataFrame): The Polars DataFrame.
            path (PathLike): The path to the Parquet file.
        """
        raise NotImplementedError


class BaseRepository(ABC):
    """Base class for repositories."""

    @abstractmethod
    def read_as_polars(self) -> pl.DataFrame:
        """Read data as a Polars DataFrame.

        Returns:
            pl.DataFrame: The Polars DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, id_: str) -> list[dict]:
        """Get data by ID.

        Args: -----
            id_ (str): The ID of the data.

        Returns:
            list[dict]: Records that match the ID.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> list[dict]:
        """Get data by name.

        Args: -----
            name (str): The name of the data.

        Returns:
            list[dict]: Records that match the name.
        """
        raise NotImplementedError
