"""Contains domain service for location business logic."""

import polars as pl


class LocationDomainService:
    """Domain service for location business rules."""

    @staticmethod
    def check_duplicate_id(df: pl.DataFrame, id_: str) -> bool:
        """Check if a location ID already exists in the DataFrame.

        Args: -----
            df (pl.DataFrame): The locations DataFrame.
            id_ (str): The ID to check.

        Returns:
            bool: True if the ID already exists.
        """
        return df.filter(pl.col("id") == id_).height > 0

    @staticmethod
    def generate_next_id(df: pl.DataFrame) -> str:
        """Generate the next sequential string ID based on the max existing ID.

        Args: -----
            df (pl.DataFrame): The locations DataFrame.

        Returns:
            str: The next sequential ID as a string.
        """
        if df.is_empty():
            return "1"
        max_id = df["id"].cast(pl.Int64).max()
        return str(max_id + 1)
