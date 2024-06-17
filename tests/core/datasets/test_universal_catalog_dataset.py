from pathlib import PurePosixPath

import pytest
import requests
import pandas as pd
from pandas.testing import assert_frame_equal

from kedro.io.core import DatasetError

from universal_catalog.core.datasets.universal_catalog_dataset import (
    UniversalCatalogDataset,
)

TEST_URL = "http://localhost:5000/"
TEST_METHOD = "POST"

BAD_TEST_URL = "http://localhost:5001/"


@pytest.fixture
def filepath_csv(tmp_path):
    return (tmp_path / "test.csv").as_posix()


@pytest.fixture
def catalog_context(filepath_csv):
    return f"""
{{
  "type": "pandas.CSVDataset",
  "filepath": "{str(filepath_csv)}"
}}    
    """


@pytest.fixture
def dummy_dataframe():
    return pd.DataFrame({"col1": [1, 2], "col2": [4, 5], "col3": [5, 6]})


@pytest.fixture
def dataset():
    return UniversalCatalogDataset(url=TEST_URL, source_name="companies")


def test_universal_catalog_dataset(dataset):
    assert isinstance(dataset, UniversalCatalogDataset)


def test_materialize_and_describe(
    requests_mock, dataset, catalog_context, filepath_csv
):
    requests_mock.register_uri(
        TEST_METHOD, TEST_URL + "/dataset/", text=catalog_context
    )
    assert dataset._describe().get("filepath") == PurePosixPath(filepath_csv)


def test_save_and_load(
    requests_mock, dataset, catalog_context, filepath_csv, dummy_dataframe
):
    requests_mock.register_uri(
        TEST_METHOD, TEST_URL + "/dataset/", text=catalog_context
    )
    dataset.save(data=dummy_dataframe)
    loaded = dataset.load()
    assert_frame_equal(loaded, dummy_dataframe)


def test_http_error(requests_mock, dataset):
    requests_mock.register_uri(
        TEST_METHOD,
        TEST_URL + "/dataset/",
        text="Failed to fetch data",
        status_code=requests.codes.not_found,
    )
    with pytest.raises(DatasetError):
        UniversalCatalogDataset(url=TEST_URL, source_name="companies")._describe()


def test_os_error(dataset):
    with pytest.raises(DatasetError):
        UniversalCatalogDataset(url=BAD_TEST_URL, source_name="companies")._describe()
