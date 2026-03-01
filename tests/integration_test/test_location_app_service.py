"""Integration tests for LocationAppService with real file I/O."""

import shutil
from pathlib import Path

import polars as pl
import pytest

from src.app_service.location import LocationAppService
from src.infra.repository import StorageLocationRepository
from src.infra.storage_adapter import LocalStorageAdapter


@pytest.fixture(scope="module")
def source_location_uri() -> Path:
    """Fixture for the source location URI."""
    base_dir = Path(__file__).resolve().parents[2]
    return base_dir / "tests/integration_test/input_data/locations.csv"


@pytest.fixture
def data_uri(source_location_uri: Path, tmp_path: Path) -> Path:
    """Fixture that copies test CSV to a temp directory."""
    dest = tmp_path / "locations.csv"
    shutil.copy(source_location_uri, dest)
    return dest


@pytest.fixture
def app_service(data_uri: Path) -> LocationAppService:
    """Fixture for LocationAppService with real adapter and repository."""
    adapter = LocalStorageAdapter()
    repository = StorageLocationRepository(storage_adapter=adapter, uri=data_uri)
    return LocationAppService(repository=repository, storage_adapter=adapter, data_uri=data_uri)


class TestLocationAppServiceIntegration:
    """Integration test cases for the full CRUD round-trip."""

    def test_full_crud_round_trip(self, app_service: LocationAppService) -> None:
        """Test add, read, update, delete as a full round-trip."""
        # Read initial data
        initial = app_service.get_all_locations()
        assert initial.height == 3  # noqa: S101, PLR2004

        # Add a location
        after_add = app_service.add_location(
            id_="4", name="新規店舗", address="〒100-0001 東京都千代田区", latitude=35.6812, longitude=139.7671,
        )
        assert after_add.height == 4  # noqa: S101, PLR2004

        # Update the location
        after_update = app_service.update_location(
            id_="4", name="更新店舗", address="〒100-0002 東京都中央区", latitude=35.6895, longitude=139.6917,
        )
        assert after_update.height == 4  # noqa: S101, PLR2004
        updated_row = after_update.filter(pl.col("id") == "4")
        assert updated_row["name"].to_list() == ["更新店舗"]  # noqa: S101

        # Delete the location
        after_delete = app_service.delete_location("4")
        assert after_delete.height == 3  # noqa: S101, PLR2004

        # Verify persistence
        final = app_service.get_all_locations()
        assert final.height == 3  # noqa: S101, PLR2004

    def test_upload_csv_file(self, app_service: LocationAppService) -> None:
        """Test uploading a CSV file replaces location data when saved."""
        csv_bytes = b"id,name,address,latitude,longitude\n10,Upload Test,Test Addr,35.0,139.0\n"
        uploaded_df = app_service.upload_file(csv_bytes, "upload.csv")
        assert uploaded_df.height == 1  # noqa: S101

        app_service.save_uploaded(uploaded_df)
        result = app_service.get_all_locations()
        assert result.height == 1  # noqa: S101
        assert result["id"].to_list() == ["10"]  # noqa: S101
