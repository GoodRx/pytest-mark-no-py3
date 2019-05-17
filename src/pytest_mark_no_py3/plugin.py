import sys

import pytest

from . import MARKER

PY3 = sys.version_info.major == 3


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "%s: tests that are expected to fail on Python 3" % MARKER
    )


def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_closest_marker(MARKER):
            item.add_marker(
                pytest.mark.xfail(
                    PY3, reason="test is not compatible with Python 3", strict=True
                )
            )
