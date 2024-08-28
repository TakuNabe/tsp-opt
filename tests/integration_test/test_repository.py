"""Test cases for the StorageLocationRepository class."""

from pathlib import Path

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
