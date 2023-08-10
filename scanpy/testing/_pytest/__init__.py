"""A private pytest plugin"""
from __future__ import annotations

from collections.abc import Iterable
from types import ModuleType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pytest

from .fixtures import *  # noqa: F403


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--internet-tests",
        action="store_true",
        default=False,
        help=(
            "Run tests that retrieve stuff from the internet. "
            "This increases test time."
        ),
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: Iterable[pytest.Item]
) -> None:
    import pytest

    run_internet = config.getoption("--internet-tests")
    skip_internet = pytest.mark.skip(reason="need --internet-tests option to run")
    for item in items:
        # All tests marked with `pytest.mark.internet` get skipped unless
        # `--run-internet` passed
        if not run_internet and ("internet" in item.keywords):
            item.add_marker(skip_internet)


def pytest_itemcollected(item: pytest.Item) -> None:
    import pytest

    if not isinstance(item, pytest.DoctestItem):
        return
    func = _import_name(item.name)
    if marker := getattr(func, '_doctest_mark', None):
        item.add_marker(marker)


def _import_name(name: str) -> Any:
    from importlib import import_module

    parts = name.split('.')
    obj = import_module(parts[0])
    for i, name in enumerate(parts[1:]):
        try:
            obj = import_module(f'{obj.__name__}.{name}')
        except ModuleNotFoundError:
            break
    for name in parts[i + 1 :]:
        try:
            obj = getattr(obj, name)
        except AttributeError:
            raise RuntimeError(f'{parts[:i]}, {parts[i+1:]}, {obj} {name}')
    return obj
