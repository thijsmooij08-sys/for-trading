"""Bootstrap contract for the distributable Polytrader package."""


def test_package_exposes_a_version() -> None:
    """Removing the package version must break consumers at import time."""
    from polytrader import __version__

    assert isinstance(__version__, str)
    assert __version__
