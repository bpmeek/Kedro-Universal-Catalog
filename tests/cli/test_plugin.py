import pytest

from pathlib import Path
from click.testing import CliRunner

import shutil

from universal_catalog.cli.plugin import init, TEMPLATE_PATH


@pytest.fixture
def cookiecutter_directory() -> Path:
    return Path(TEMPLATE_PATH)


@pytest.fixture
def server_name():
    return "test-server"


def test_init(server_name, tmp_path):
    runner = CliRunner()
    result = runner.invoke(init, ["-n", server_name, "-o", str(tmp_path)])
    assert result.exit_code == 0
    _clean_up_project(tmp_path)


def test_interactive_init(server_name, tmp_path):
    runner = CliRunner()
    result = runner.invoke(init, input=f"{server_name}\n")
    assert result.exit_code == 0
    _clean_up_project(Path(f"./{server_name}"))


def test_bad_name():
    runner = CliRunner()
    result = runner.invoke(init, ["-n", "''"])
    assert result.exit_code != 0
    assert "is an invalid value for" in result.output


def test_bad_name_interactive():
    runner = CliRunner()
    result = runner.invoke(init, input="A\n")
    assert result.exit_code != 0
    assert "is an invalid value for catalog name." in result.output


def _clean_up_project(project_dir):
    if project_dir.is_dir():
        shutil.rmtree(str(project_dir), ignore_errors=True)
