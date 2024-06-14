import pytest

from universal_catalog.core.serving import load_server_settings


SETTINGS_CONTEXT = """
host: 127.0.0.1
port: 8000
"""


@pytest.fixture
def tmp_settings(tmp_path):
    tmp_dir = tmp_path / "base"
    tmp_dir.mkdir()
    settings_file = tmp_dir / "serving.yml"
    settings_file.write_text(SETTINGS_CONTEXT)
    return {"path": tmp_path}


def test_load_server_settings(tmp_settings):
    server_settings = load_server_settings(tmp_settings)
    assert server_settings["host"] == "127.0.0.1"
    assert server_settings["port"] == 8000
