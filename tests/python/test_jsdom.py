"""
Tests for Obsplot jsdom file output.
"""

import io
import pickle

import pytest

from pyobsplot import Obsplot
from pyobsplot.utils import DEFAULT_THEME


@pytest.fixture(scope="module")
def op():
    op = Obsplot(format="html")
    yield op
    op._jsdom_close()  # type: ignore


@pytest.fixture(scope="module")
def specs():
    with open("tests/python/reference/specs.pkl", "rb") as f:
        specs = pickle.load(f)
    return specs


@pytest.fixture(scope="module")
def themes():
    with open("tests/python/reference/themes.pkl", "rb") as f:
        themes = pickle.load(f)
    return themes


@pytest.fixture(scope="module")
def defaults():
    with open("tests/python/reference/defaults.pkl", "rb") as f:
        defaults = pickle.load(f)
    return defaults


class TestSpecs:
    def test_jsdom_plots(self, op, specs, themes, defaults):
        results = {}
        for key, spec in specs.items():
            out = io.StringIO()
            if key in themes:
                op.theme = themes[key]
            else:
                op.theme = DEFAULT_THEME
            if key in defaults:
                op.default = defaults[key]
            else:
                op.default = {}
            op(spec, path=out)
            with open(f"tests/python/reference/{key}") as f:
                results[key] = out.getvalue() == f.read()
            out.close()
        assert all(results)
