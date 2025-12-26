def test_cli_importable():
    # Basic smoke import to ensure CLI module loads without side-effects
    import importlib
    importlib.import_module('jsscanner.__main__')
    assert True
