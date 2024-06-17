from __future__ import annotations

import requests
import json

from kedro.io.core import DatasetError


def _execute_request(url: str, json_obj: dict[str, str] | None) -> requests.Response:
    try:
        response = requests.post(url, data=json.dumps(json_obj))
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise DatasetError("Failed to fetch data", exc) from exc
    except OSError as exc:
        raise DatasetError("Failed to connect to the remote server", exc) from exc

    return response
