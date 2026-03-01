"""Test cases for the StorageLocationRepository class."""

import shutil
from pathlib import Path

import polars as pl
import pytest

from src.infra.repository import StorageLocationRepository
from src.infra.storage_adapter import LocalStorageAdapter


@pytest.fixture(scope="module")
def source_location_uri() -> Path:
    """Fixture for the source location URI."""
    base_dir = Path(__file__).resolve().parents[2]
    return base_dir / "tests/integration_test/input_data/locations.csv"


@pytest.fixture(scope="module")
def local_storage_adapter() -> LocalStorageAdapter:
    """Fixture for the storage adapter."""
    return LocalStorageAdapter()


class TestStorageLocationRepository:
    """Test cases for the StorageLocationRepository class."""

    @pytest.fixture(scope="class", autouse=False)
    def repository(
        self, source_location_uri: Path, local_storage_adapter: LocalStorageAdapter
    ) -> StorageLocationRepository:
        """Fixture for the StorageLocationRepository class."""
        return StorageLocationRepository(
            storage_adapter=local_storage_adapter,
            uri=source_location_uri,
        )

    def test_read_as_polars(self, repository: StorageLocationRepository) -> None:
        """Test the read_as_polars method."""
        df_res = repository.read_as_polars()
        assert df_res.shape == (3, 5)  # noqa: S101

    def test_get_by_id(self, repository: StorageLocationRepository) -> None:
        """Test the get_by_id method."""
        res = repository.get_by_id("1")
        assert len(res) == 1  # noqa: S101
        assert res[0]["id"] == "1"  # noqa: S101

    def test_get_by_name(self, repository: StorageLocationRepository) -> None:
        """Test the get_by_name method."""
        res = repository.get_by_name("ファミリーマートA")
        assert isinstance(res, list)  # noqa: S101
        assert len(res) == 1  # noqa: S101
        assert res[0]["name"] == "ファミリーマートA"  # noqa: S101


class TestStorageLocationRepositoryWrite:
    """Test cases for the write methods of StorageLocationRepository."""

    @pytest.fixture
    def writable_uri(self, source_location_uri: Path, tmp_path: Path) -> Path:
        """Fixture that copies the test CSV to a temp directory for write tests."""
        dest = tmp_path / "locations.csv"
        shutil.copy(source_location_uri, dest)
        return dest

    @pytest.fixture
    def writable_repository(
        self, writable_uri: Path, local_storage_adapter: LocalStorageAdapter
    ) -> StorageLocationRepository:
        """Fixture for a writable StorageLocationRepository."""
        return StorageLocationRepository(
            storage_adapter=local_storage_adapter,
            uri=writable_uri,
        )

    def test_save_overwrites_existing_data(self, writable_repository: StorageLocationRepository) -> None:
        """Test that save replaces all existing data with the given DataFrame."""
        new_df = pl.DataFrame(
            {
                "id": ["10"],
                "name": ["テスト店舗"],
                "address": ["〒100-0001 東京都千代田区"],
                "latitude": [35.6812],
                "longitude": [139.7671],
            },
        )
        writable_repository.save(new_df)

        result = writable_repository.read_as_polars()
        assert result.shape == (1, 5)  # noqa: S101
        assert result["id"].to_list() == ["10"]  # noqa: S101

    def test_delete_by_id_removes_matching_row(self, writable_repository: StorageLocationRepository) -> None:
        """Test that delete_by_id removes the row with the given ID and persists."""
        result = writable_repository.delete_by_id("1")

        assert result.shape == (2, 5)  # noqa: S101
        assert "1" not in result["id"].to_list()  # noqa: S101

        # Verify persistence by re-reading
        re_read = writable_repository.read_as_polars()
        assert re_read.shape == (2, 5)  # noqa: S101

    def test_delete_by_id_with_nonexistent_id_removes_nothing(
        self, writable_repository: StorageLocationRepository
    ) -> None:
        """Test that delete_by_id with a non-existent ID leaves data unchanged."""
        result = writable_repository.delete_by_id("999")
        assert result.shape == (3, 5)  # noqa: S101
