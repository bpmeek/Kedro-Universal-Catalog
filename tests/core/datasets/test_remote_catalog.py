import pytest

from .test_universal_catalog_dataset import TEST_URL, TEST_METHOD

from kedro.io.data_catalog import DataCatalog
from kedro.io.core import DatasetError
from universal_catalog import RemoteCatalog


@pytest.fixture
def remote_catalog():
    return RemoteCatalog()


@pytest.fixture
def credentials():
    return dict(remote_catalog=dict(url=TEST_URL))


@pytest.fixture
def bad_credentials():
    return {}


@pytest.fixture
def missing_url():
    return dict(remote_catalog={"bad_url": "bad"})


@pytest.fixture
def catalog_json():
    return '{"companies": {"type": "pandas.CSVDataset", "filepath": "data/01_raw/companies.csv"}}'


@pytest.fixture
def update_catalog_dict():
    return dict(
        cars=dict(type="pandas.CSVDataset", filepath="data/01_raw/companies.csv")
    )


def test_remote_catalog(remote_catalog):
    assert isinstance(remote_catalog, DataCatalog)


def test_bad_credentials(bad_credentials):
    with pytest.raises(DatasetError):
        RemoteCatalog.from_config(catalog=None, credentials=bad_credentials)


def test_missing_url(missing_url):
    with pytest.raises(DatasetError):
        RemoteCatalog.from_config(catalog=None, credentials=missing_url)


def test_load_remote_catalog(requests_mock, catalog_json, credentials):
    requests_mock.register_uri(TEST_METHOD, TEST_URL + "/catalog/", text=catalog_json)
    remote_catalog = RemoteCatalog.from_config(catalog=None, credentials=credentials)
    assert isinstance(remote_catalog, DataCatalog)
    assert "companies" in remote_catalog._datasets


def test_update(requests_mock, catalog_json, credentials, update_catalog_dict):
    requests_mock.register_uri(TEST_METHOD, TEST_URL + "/catalog/", text=catalog_json)
    remote_catalog = RemoteCatalog.from_config(
        catalog=update_catalog_dict, credentials=credentials
    )
    assert isinstance(remote_catalog, DataCatalog)
    assert "companies" in remote_catalog._datasets
    assert "cars" in remote_catalog._datasets
