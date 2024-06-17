import pytest
import yaml

from universal_catalog.core.universal_catalog import load_catalog, UniversalCatalog
from kedro.io.core import DatasetNotFoundError


CATALOG_CONTEXT = """
companies:
  type: pandas.CSVDataset
  filepath: data/01_raw/companies.csv
"""


@pytest.fixture
def tmp_settings(tmp_path):
    tmp_dir = tmp_path / "base"
    tmp_dir.mkdir()
    settings_file = tmp_dir / "catalog.yml"
    settings_file.write_text(CATALOG_CONTEXT)
    return {"path": tmp_path}


@pytest.fixture
def tmp_catalog(tmp_settings):
    return load_catalog(tmp_settings)


def test_load_catalog(tmp_settings, tmp_catalog):
    assert isinstance(tmp_catalog, UniversalCatalog)


def test_config_string(tmp_catalog: UniversalCatalog):
    yml = tmp_catalog.config_string()
    assert yml.strip() == CATALOG_CONTEXT.strip()


def test_get_entry(tmp_catalog: UniversalCatalog):
    entry = tmp_catalog.get_entry("companies")
    assert entry["filepath"] == "data/01_raw/companies.csv"
    assert entry["type"] == "pandas.CSVDataset"


def test_bad_entry(tmp_catalog: UniversalCatalog):
    with pytest.raises(DatasetNotFoundError):
        tmp_catalog.get_entry("companie")


def test_get_catalog(tmp_catalog: UniversalCatalog):
    catalog = tmp_catalog.get_catalog()
    catalog_dict = yaml.safe_load(CATALOG_CONTEXT)
    assert catalog_dict == catalog
