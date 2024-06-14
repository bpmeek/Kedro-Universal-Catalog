from __future__ import annotations

from typing import Any

import requests
from kedro.io.core import AbstractDataset, DatasetError

import json


class UniversalCatalogDataset(AbstractDataset):
    """``UniversalCatalogDataset`` is a wrapper around the ``AbstractDataset``
    it uses the provided config entry to implement the dataset received from
    the Universal Catalog Server and exposes the _load, _save, and _describe
    functions from that specific dataset.

    Example usage for the `YAML API <https://kedro.readthedocs.io/en/stable/data/\
    data_catalog_yaml_examples.html>`_:

    .. code-block:: yaml

        cars:
            type: universal_catalog.UniversalCatalogDataset
            url: http://localhost:5000/

    Example usage for the
    `Python API <https://kedro.readthedocs.io/en/stable/data/\
    advanced_data_catalog_usage.html>`_:

    .. code-block:: python

        >>> from universal_catalog import UniversalCatalogDataset
        >>>
        >>>
        >>> dataset = UniversalCatalogDataset(
        ...     url="http://localhost:5000/",
        ...)
        >>> data = dataset.load()

    """

    def __init__(self, url: str, source_name: str):
        self._url = f"{url}/dataset/"
        self._source_name = source_name
        self._dataset = None

    def _materialize(self):
        if not self._dataset:
            request_body = dict(name=self._source_name)
            _config: dict[str, Any] = self._execute_request(request_body).json()
            self._dataset = AbstractDataset.from_config(
                name=self._source_name, config=_config
            )

    def _execute_request(self, json_obj: dict[str, str]) -> requests.Response:
        try:
            response = requests.post(self._url, data=json.dumps(json_obj))
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise DatasetError("Failed to fetch data", exc) from exc
        except OSError as exc:
            raise DatasetError("Failed to connect to the remote server", exc) from exc

        return response

    def _load(self):
        self._materialize()
        return self._dataset.load()

    def _save(self, data):
        self._materialize()
        self._dataset.save(data)

    def _describe(self):
        self._materialize()
        return self._dataset._describe()
