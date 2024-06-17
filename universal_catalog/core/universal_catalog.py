from __future__ import annotations

from typing import Any, Dict

from omegaconf import OmegaConf
from pathlib import Path

from kedro.io.data_catalog import DataCatalog
from kedro.io.core import DatasetNotFoundError

import copy
import difflib


def load_catalog(
    config_path: dict[str, Path], environment: str = "base"
) -> UniversalCatalog:
    catalog_path = config_path.get("path") / f"{environment}/catalog.yml"
    catalog = OmegaConf.load(catalog_path)
    catalog = OmegaConf.to_object(catalog)
    return UniversalCatalog().from_config(catalog)


class UniversalCatalog(DataCatalog):
    def __init__(
        self, catalog: dict[str, dict[str, Any]] | None = None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._datasets = catalog

    @classmethod
    def from_config(
        cls,
        catalog: dict[str, dict[str, Any]] | None,
        credentials: dict[str, dict[str, Any]] | None = None,
        load_versions: dict[str, str] | None = None,
        save_version: str | None = None,
    ) -> UniversalCatalog:
        # Verify config by using config to initialize ``DataCatalog``
        super().from_config(
            catalog=catalog,
            credentials=credentials,
            load_versions=load_versions,
            save_version=save_version,
        )
        return cls(catalog=catalog)

    def config_string(self):
        config = OmegaConf.create(self._datasets)
        return OmegaConf.to_yaml(config)

    def get_entry(self, dataset_name: str, suggest: bool = True) -> Dict[str, Any]:
        """
        Copy of ``DataCatalog._get_dataset()`` but avoids loading abstract dataset
        Args:
            dataset_name: str
                Name of the dataset to search the catalog for.
            suggest: bool
                Whether to suggest similarly named objects if `dataset_name` is not
                found

        Returns: Dict[str, Any]
            Entry associated with `dataset_name` if found.
            If not found and `suggest` is `False` `None` is returned, otherwise
            similar named matches are returned.


        """
        matched_pattern = self._match_pattern(
            self._dataset_patterns, dataset_name
        ) or self._match_pattern(self._default_pattern, dataset_name)
        if dataset_name not in self._datasets and matched_pattern:  # pragma: no cover
            # If the dataset is a patterned dataset, materialise it and add it to
            # the catalog
            config_copy = copy.deepcopy(
                self._dataset_patterns.get(matched_pattern)
                or self._default_pattern.get(matched_pattern)
                or {}
            )
            dataset_config = self._resolve_config(
                dataset_name, matched_pattern, config_copy
            )
            if (
                self._specificity(matched_pattern) == 0
                and matched_pattern in self._default_pattern
            ):
                self._logger.warning(
                    "Config from the dataset factory pattern '%s' in the catalog will be used to "
                    "override the default dataset creation for '%s'",
                    matched_pattern,
                    dataset_name,
                )
            return dataset_config
        if dataset_name not in self._datasets:
            error_msg = f"Dataset '{dataset_name}' not found in the catalog"

            # Flag to turn on/off fuzzy-matching which can be time consuming and
            # slow down plugins like `kedro-viz`
            if suggest:
                matches = difflib.get_close_matches(dataset_name, self._datasets.keys())
                if matches:
                    suggestions = ", ".join(matches)
                    error_msg += f" - did you mean one of these instead: {suggestions}"
            raise DatasetNotFoundError(error_msg)

        dataset_config = self._datasets.get(dataset_name, None)

        return dataset_config

    def get_catalog(self) -> dict[str, dict[str, Any]]:
        """Return dictionary of catalog entries."""
        return self._datasets
