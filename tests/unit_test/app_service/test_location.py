"""Unit tests for LocationAppService."""

from unittest.mock import MagicMock

import pandera as pa
import polars as pl
import pytest
from pydantic import ValidationError

from src.app_service.location import LocationAppService


@pytest.fixture
def sample_df() -> pl.DataFrame:
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


@pytest.fixture
def mock_repository(sample_df: pl.DataFrame) -> MagicMock:
    """Fixture for a mocked writable repository."""
    repo = MagicMock()
    repo.read_as_polars.return_value = sample_df
    repo.save.return_value = None
    return repo


@pytest.fixture
def mock_storage_adapter() -> MagicMock:
    """Fixture for a mocked storage adapter."""
    return MagicMock()


@pytest.fixture
def service(mock_repository: MagicMock, mock_storage_adapter: MagicMock) -> LocationAppService:
    """Fixture for the LocationAppService."""
    return LocationAppService(
        repository=mock_repository,
        storage_adapter=mock_storage_adapter,
        data_uri="/tmp/test_locations.csv",  # noqa: S108
    )


class TestGetAllLocations:
    """Test cases for get_all_locations."""

    def test_returns_dataframe_from_repository(self, service: LocationAppService, sample_df: pl.DataFrame) -> None:
        """Test that get_all_locations returns the DataFrame from the repository."""
        result = service.get_all_locations()
        assert result.shape == sample_df.shape  # noqa: S101

    def test_returns_empty_dataframe_when_file_not_found(
        self, mock_repository: MagicMock, mock_storage_adapter: MagicMock
    ) -> None:
        """Test that get_all_locations returns an empty DataFrame when file is missing."""
        mock_repository.read_as_polars.side_effect = FileNotFoundError
        svc = LocationAppService(
            repository=mock_repository,
            storage_adapter=mock_storage_adapter,
            data_uri="/tmp/missing.csv",  # noqa: S108
        )
        result = svc.get_all_locations()
        assert result.is_empty()  # noqa: S101


class TestAddLocation:
    """Test cases for add_location."""

    def test_adds_location_and_saves(self, service: LocationAppService, mock_repository: MagicMock) -> None:
        """Test that add_location appends a row and calls save."""
        result = service.add_location(
            id_="4", name="新店舗", address="新住所", latitude=35.3, longitude=139.3,
        )
        assert result.height == 4  # noqa: S101, PLR2004
        mock_repository.save.assert_called_once()

    def test_rejects_duplicate_id(self, service: LocationAppService) -> None:
        """Test that add_location raises ValueError for a duplicate ID."""
        with pytest.raises(ValueError, match="already exists"):
            service.add_location(
                id_="1", name="重複店舗", address="住所", latitude=35.0, longitude=139.0,
            )

    def test_rejects_invalid_coordinates(self, service: LocationAppService) -> None:
        """Test that add_location raises ValidationError for invalid coordinates."""
        with pytest.raises(ValidationError):
            service.add_location(
                id_="99", name="無効店舗", address="住所", latitude=999.0, longitude=139.0,
            )


class TestUpdateLocation:
    """Test cases for update_location."""

    def test_updates_existing_location(self, service: LocationAppService, mock_repository: MagicMock) -> None:
        """Test that update_location replaces the row and saves."""
        result = service.update_location(
            id_="1", name="更新店舗", address="更新住所", latitude=35.5, longitude=139.5,
        )
        assert result.height == 3  # noqa: S101, PLR2004
        assert result.filter(pl.col("id") == "1")["name"].to_list() == ["更新店舗"]  # noqa: S101
        mock_repository.save.assert_called_once()

    def test_rejects_nonexistent_id(self, service: LocationAppService) -> None:
        """Test that update_location raises ValueError for a non-existent ID."""
        with pytest.raises(ValueError, match="not found"):
            service.update_location(
                id_="999", name="存在しない", address="住所", latitude=35.0, longitude=139.0,
            )


class TestDeleteLocation:
    """Test cases for delete_location."""

    def test_deletes_location(self, service: LocationAppService, mock_repository: MagicMock) -> None:
        """Test that delete_location delegates to repository.delete_by_id."""
        mock_repository.delete_by_id.return_value = pl.DataFrame(
            {
                "id": ["2", "3"],
                "name": ["店舗B", "店舗C"],
                "address": ["住所B", "住所C"],
                "latitude": [35.1, 35.2],
                "longitude": [139.1, 139.2],
            },
        )
        result = service.delete_location("1")
        assert result.height == 2  # noqa: S101, PLR2004
        mock_repository.delete_by_id.assert_called_once_with("1")


class TestUploadFile:
    """Test cases for upload_file."""

    def test_upload_valid_csv(self, service: LocationAppService) -> None:
        """Test that upload_file parses and validates a valid CSV."""
        csv_content = b"id,name,address,latitude,longitude\n10,Test,Addr,35.0,139.0\n"
        result = service.upload_file(csv_content, "locations.csv")
        assert result.height == 1  # noqa: S101
        assert result["id"].to_list() == ["10"]  # noqa: S101

    def test_upload_invalid_csv_raises_error(self, service: LocationAppService) -> None:
        """Test that upload_file raises an error for invalid CSV data."""
        csv_content = b"bad_col1,bad_col2\nval1,val2\n"
        with pytest.raises((pa.errors.SchemaError, pl.exceptions.ColumnNotFoundError)):
            service.upload_file(csv_content, "bad.csv")
