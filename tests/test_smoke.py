"""Smoke test: package imports cleanly. Replace/extend as modules land."""

import tracewright


def test_version_is_set() -> None:
    assert tracewright.__version__
