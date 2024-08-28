"""Mixin classes for schema models."""

import polars as pl


class DataFrameModelMixin:
    """Mixin class for schema models."""

    @classmethod
    def get_dtypes(cls) -> dict[str, pl.DataType]:
        """Convert the schema model to a Polars schema.

        Returns:
            dict[str, pl.DataType]: The Polars schema.
        """
        return cls.to_schema().dtypes
