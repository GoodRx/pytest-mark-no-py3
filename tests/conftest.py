from click.testing import CliRunner
import pytest

pytest_plugins = "pytester"


@pytest.fixture
def runner():
    return CliRunner()
