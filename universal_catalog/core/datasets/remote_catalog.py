from __future__ import annotations

from kedro.io import DataCatalog
from kedro.io.core import DatasetError

from typing import Any

from .utils import _execute_request


class RemoteCatalog(DataCatalog):
    """``RemoteCatalog`` is a DataCatalog subclass that overrides the
    `from_config` class method to fetch the entire remote catalog
    and merge it with the DataCatalog from your project.
    If a dataset is present in both the remote catalog and the project catalog
    the project catalog entry is kept.
    """

    def __init__(self):
        super().__init__()

    @classmethod
    def from_config(
        cls,
        catalog: dict[str, dict[str, Any]] | None,
        credentials: dict[str, dict[str, Any]] | None = None,
        load_versions: dict[str, str] | None = None,
        save_version: str | None = None,
    ) -> DataCatalog:
        if "remote_catalog" not in credentials.keys():
            raise DatasetError(
                "`remote_catalog` must be provided in credentials.\nAlong with url."
            )
        if "url" not in credentials["remote_catalog"].keys():
            raise DatasetError("`url` must be provided in `remote_catalog` entry.")
        url = credentials["remote_catalog"]["url"]
        url = url + "/catalog/"
        cfg = _execute_request(url, None).json()
        cfg.update(catalog or {})
        return DataCatalog.from_config(cfg, credentials, load_versions, save_version)
