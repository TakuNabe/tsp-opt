"""Unit tests for LocationDomainService."""

import polars as pl
import pytest

from src.domain.service.location import LocationDomainService


class TestLocationDomainService:
    """Test cases for the LocationDomainService class."""

    @pytest.fixture
    def sample_df(self) -> pl.DataFrame:
        """Fixture for a sample locations DataFrame."""
        return pl.DataFrame(
            {
                "id": ["1", "2", "3"],
                "name": ["店舗A", "店舗B", "店舗C"],
                "address": ["住所A", "住所B", "住所C"],
                "latitude": [35.0, 35.1, 35.2],
                "longitude": [139.0, 139.1, 139.2],
            },
        )

    def test_check_duplicate_id_returns_true_for_existing_id(self, sample_df: pl.DataFrame) -> None:
        """Test that check_duplicate_id returns True when the ID already exists."""
        result = LocationDomainService.check_duplicate_id(sample_df, "1")
        assert result is True  # noqa: S101

    def test_check_duplicate_id_returns_false_for_new_id(self, sample_df: pl.DataFrame) -> None:
        """Test that check_duplicate_id returns False when the ID does not exist."""
        result = LocationDomainService.check_duplicate_id(sample_df, "999")
        assert result is False  # noqa: S101

    def test_generate_next_id_returns_incremented_id(self, sample_df: pl.DataFrame) -> None:
        """Test that generate_next_id returns the next sequential string ID."""
        result = LocationDomainService.generate_next_id(sample_df)
        assert result == "4"  # noqa: S101

    def test_generate_next_id_returns_one_for_empty_df(self) -> None:
        """Test that generate_next_id returns '1' for an empty DataFrame."""
        empty_df = pl.DataFrame(
            {
                "id": [],
                "name": [],
                "address": [],
                "latitude": [],
                "longitude": [],
            },
            schema={
                "id": pl.Utf8,
                "name": pl.Utf8,
                "address": pl.Utf8,
                "latitude": pl.Float64,
                "longitude": pl.Float64,
            },
        )
        result = LocationDomainService.generate_next_id(empty_df)
        assert result == "1"  # noqa: S101
