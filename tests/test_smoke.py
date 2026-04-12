"""Smoke test — proves the package installs and imports."""

import aegis_rmf


def test_version_exists():
    assert aegis_rmf.__version__ == "0.1.0"
