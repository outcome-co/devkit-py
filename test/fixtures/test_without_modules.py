import pytest


def test_import():
    import rich  # type: ignore # noqa: F401, WPS433


@pytest.mark.parametrize('modules_to_hide', [['rich']])
@pytest.mark.usefixtures('with_hidden_modules')
def test_import_error():
    with pytest.raises(ImportError):
        import rich  # type: ignore # noqa: F401, WPS433
