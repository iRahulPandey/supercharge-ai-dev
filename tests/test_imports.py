"""Smoke tests for package imports."""


def test_package_imports():
    """Test that supercharge_ai package imports without error."""
    import supercharge_ai
    assert supercharge_ai.__version__ == "0.0.1"


def test_config_module_imports():
    """Test that config module imports without error."""
    from supercharge_ai.config import ProjectConfig, load_config
    assert ProjectConfig is not None
    assert load_config is not None
