from app.config import Settings


def test_settings_read_neo4j_values_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("NEO4J_URI", "bolt://graph:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "test-user")
    monkeypatch.setenv("NEO4J_PASSWORD", "test-password")

    settings = Settings()

    assert settings.neo4j_uri == "bolt://graph:7687"
    assert settings.neo4j_username == "test-user"
    assert settings.neo4j_password == "test-password"
