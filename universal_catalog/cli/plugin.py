from __future__ import annotations

import shutil

import click
import re
import sys

import universal_catalog
from universal_catalog import __version__ as version
from pathlib import Path
import yaml
from kedro.framework.cli.utils import KedroCliError

from collections import OrderedDict

from typing import Any

KEDRO_CATALOG_PATH = Path(universal_catalog.__file__).parent
TEMPLATE_PATH = KEDRO_CATALOG_PATH / "templates" / "server"


@click.group()
def cli():  # pragma: no cover
    pass


@cli.command("init")
@click.option("--name", "-n", "server_name")
@click.option("--output", "-o", "output_dir")
def init(server_name: str, output_dir: str) -> None:
    """Creates a new Universal Catalog project."""
    defaults = {"output_dir": output_dir or str(Path.cwd().resolve())}
    cookiecutter_dir = Path(TEMPLATE_PATH)
    prompts_required = _get_prompts(cookiecutter_dir, server_name)
    cookiecutter_context = _get_cookiecutter_context(cookiecutter_dir)

    extra_context = _get_context(prompts_required, cookiecutter_context, server_name)
    cookiecutter_args = {
        "output_dir": defaults.get("output_dir"),
        "no_input": True,
        "extra_context": extra_context,
    }

    _create_catalog(str(cookiecutter_dir), cookiecutter_args)


def _get_prompts(cookiecutter_dir: Path, server_name: str | None) -> Any:
    prompts_yml = cookiecutter_dir / "prompts.yml"
    if not prompts_yml.is_file():
        return {}  # pragma: no cover
    try:
        with prompts_yml.open("r") as f:
            prompts_required = yaml.safe_load(f)
    except Exception as e:  # pragma: no cover
        raise KedroCliError(
            "Failed to generate Catalog: could not load prompts.yml."
        ) from e

    if server_name is not None:
        _validate_input_with_regex_pattern("server_name", server_name)
        del prompts_required["server_name"]

    return prompts_required


def _get_context(
    prompts_required: dict,
    cookiecutter_context: OrderedDict | None,
    server_name: str | None,
) -> Any:
    extra_context = _fetch_config_from_user_prompts(
        prompts_required, cookiecutter_context
    )
    if server_name is not None:
        extra_context["server_name"] = server_name
    extra_context.setdefault("server_version", version)
    return extra_context


def _fetch_config_from_user_prompts(
    prompts: dict[str, Any], cookiecutter_context: OrderedDict | None
) -> dict[str, str]:
    from cookiecutter.environment import StrictEnvironment
    from cookiecutter.prompt import read_user_variable, render_variable

    if not cookiecutter_context:  # pragma: no cover
        raise Exception("No cookiecutter context provided")

    config: dict[str, str] = {}

    for variable, prompt in prompts.items():
        prompt = _Prompt(**prompt)

        cookiecutter_variable = render_variable(
            env=StrictEnvironment(context=cookiecutter_context),
            raw=cookiecutter_context.get(variable),
            cookiecutter_dict=config,
        )

        user_input = read_user_variable(str(prompt), cookiecutter_variable)
        if user_input:
            prompt.validate(user_input)
            config[variable] = user_input
    return config


class _Prompt:
    """Represent a single CLI prompt for `kedro new`"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: unused-argument
        try:
            self.title = kwargs["title"]
        except KeyError as exc:  # pragma: no cover
            raise KedroCliError(
                "Each prompt must have a title field to be valid."
            ) from exc

        self.text = kwargs.get("text", "")
        self.regexp = kwargs.get("regex_validator", None)
        self.error_message = kwargs.get("error_message", "")

    def __str__(self) -> str:
        title = self.title.strip().title()
        title = click.style(title + "\n" + "=" * len(title), bold=True)
        prompt_lines = [title] + [self.text]
        prompt_text = "\n".join(str(line).strip() for line in prompt_lines)
        return f"\n{prompt_text}\n"

    def validate(self, user_input: str) -> None:
        """Validate a given prompt value against the regex validator"""

        if self.regexp and not re.match(self.regexp, user_input.lower()):
            message = f"'{user_input}' is an invalid value for {self.title.lower()}."
            click.secho(message, fg="red", err=True)
            click.secho(self.error_message, fg="red", err=True)
            sys.exit(1)


def _validate_input_with_regex_pattern(pattern_name: str, input: str) -> None:
    VALIDATION_PATTERNS = {
        "server_name": {
            "regex": r"^[\w -]{2,}$",
            "error_message": f"'{input}' is an invalid value for catalog name. It must contain only alphanumeric symbols, spaces, underscores and hyphens and be at least 2 characters long",
        }
    }

    if not re.match(VALIDATION_PATTERNS[pattern_name]["regex"], input, flags=re.X):
        click.secho(
            VALIDATION_PATTERNS[pattern_name]["error_message"],
            fg="red",
            err=True,
        )
        sys.exit(1)


def _get_cookiecutter_context(cookiecutter_dir: Path) -> OrderedDict:
    from cookiecutter.generate import generate_context

    cookiecutter_context = generate_context(cookiecutter_dir / "cookiecutter.json")
    return cookiecutter_context.get("cookiecutter", {})


def _create_catalog(cookiecutter_dir: str, cookiecutter_args: dict[str, Any]) -> None:
    """Creates a new Kedro Universal Catalog using cookiecutter"""
    from cookiecutter.main import cookiecutter

    try:
        result_path = cookiecutter(template=cookiecutter_dir, **cookiecutter_args)
    except Exception as exc:  # pragma: no cover
        raise KedroCliError(
            "Failed to generate catalog when running cookiecutter."
        ) from exc

    _clean_pycache(Path(result_path))
    extra_context = cookiecutter_args["extra_context"]
    server_name = extra_context.get("server_name", "New Kedro Catalog")

    # print success message
    click.secho(
        "\nCongratulations!"
        f"\nYour catalog '{server_name}' has been created in the directory \n{result_path}\n"
    )


def _clean_pycache(path: Path) -> None:  # pragma: no cover
    to_delete = [each.resolve() for each in path.rglob("__pycache__")]
    for each in to_delete:
        shutil.rmtree(each, ignore_errors=True)
