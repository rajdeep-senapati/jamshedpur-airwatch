from pathlib import Path


def test_project_package_exists() -> None:
    """The importable application package should exist in the repository."""
    assert (Path(__file__).parents[1] / "src" / "airwatch" / "__init__.py").is_file()


def test_env_example_documents_no_api_key_requirement() -> None:
    """The example must accurately document the API requirements."""
    example = Path(__file__).parents[1] / ".env.example"
    assert example.is_file()
    content = example.read_text(encoding="utf-8")
    assert "does not require an API key" in content
    assert "intentionally contains none" in content
