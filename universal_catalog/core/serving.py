from pathlib import Path
from omegaconf import OmegaConf

from typing import Any, Dict


def load_server_settings(
    config_path: Dict[str, Path], environment: str = "base"
) -> Dict[str, Any]:
    server_settings_path = config_path.get("path") / f"{environment}/serving.yml"
    _server_settings = OmegaConf.load(server_settings_path)
    return OmegaConf.to_object(_server_settings)
