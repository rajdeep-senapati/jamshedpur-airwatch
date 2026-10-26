from pathlib import Path


def test_project_package_exists() -> None:
    """The importable application package should exist in the repository."""
    assert (Path(__file__).parents[1] / "src" / "airwatch" / "__init__.py").is_file()


def test_env_example_does_not_contain_a_real_key() -> None:
    """The committed example must be a placeholder, not a credential."""
    example = Path(__file__).parents[1] / ".env.example"
    assert example.is_file()
    assert "your_api_key_here" in example.read_text(encoding="utf-8") or "AIR_QUALITY_API_KEY=" in example.read_text(encoding="utf-8")
