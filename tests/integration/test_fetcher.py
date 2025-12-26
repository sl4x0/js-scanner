def test_fetcher_module_importable():
    # Basic import smoke test
    import importlib
    importlib.import_module('jsscanner.strategies.active')
    assert True
