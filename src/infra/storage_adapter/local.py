"""Contains the LocalStorageAdapter class."""

import polars as pl

from src.infra._base import BaseStorageAdapter, PathLike


class LocalStorageAdapter(BaseStorageAdapter):
    """Storage adapter for local file operations."""

    def read_csv_as_polars(self, path: str, **kwargs: dict) -> pl.DataFrame:
        """Read a CSV file as a Polars DataFrame.

        Args:
            path (str): The path to the CSV file.
            **kwargs: Additional arguments for the read_csv method.

        Returns:
            pl.DataFrame: The Polars DataFrame.
        """
        return pl.read_csv(path, **kwargs)

    def read_parquet_as_polars(self, path: str, **kwargs: dict) -> pl.DataFrame:
        """Read a Parquet file as a Polars DataFrame.

        Args:
            path (str): The path to the Parquet file.
            **kwargs: Additional arguments for the read_parquet method.

        Returns:
            pl.DataFrame: The Polars DataFrame.
        """
        return pl.read_parquet(path, **kwargs)

    def write_polars_as_csv(self, df: pl.DataFrame, path: PathLike, **kwargs: dict) -> None:
        """Write a Polars DataFrame as a CSV file.

        Args:
            df (pl.DataFrame): The Polars DataFrame.
            path (PathLike): The path to the CSV file.
            **kwargs: Additional arguments for the write_csv method.
        """
        df.write_csv(path, **kwargs)

    def write_polars_as_parquet(self, df: pl.DataFrame, path: PathLike, **kwargs: dict) -> None:
        """Write a Polars DataFrame as a Parquet file.

        Args:
            df (pl.DataFrame): The Polars DataFrame.
            path (PathLike): The path to the Parquet file.
            **kwargs: Additional arguments for the write_parquet method.
        """
        df.write_parquet(path, **kwargs)
