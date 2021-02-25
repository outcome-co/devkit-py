import pytest
from outcome.devkit.without_modules import without_modules


def test_import():
    import rich  # type: ignore # noqa: F401, WPS433


def test_import_error():
    with without_modules('rich'):
        with pytest.raises(ImportError):
            import rich  # type: ignore # noqa: F401, WPS433
