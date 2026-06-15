from pathlib import Path

from app.media_enrichment.settings import MediaEnrichmentSettings


def test_settings_load_real_youtube_secret_from_external_env_file(tmp_path: Path) -> None:
    secret_file = tmp_path / "soundatlas.env"
    secret_file.write_text(
        "\n".join(
            [
                "YOUTUBE_API_KEY=real-youtube-key",
                "SOUNDATLAS_USE_DUMMY_SERVICES=false",
            ],
        ),
        encoding="utf-8",
    )

    settings = MediaEnrichmentSettings.from_env(
        env={"SOUNDATLAS_ENV_FILE": str(secret_file)},
        codex_env_file=tmp_path / ".env.codex",
    )

    assert settings.env_source == "external"
    assert settings.env_file == secret_file
    assert settings.youtube_api_key == "real-youtube-key"
    assert settings.use_dummy_services is False
    assert settings.has_live_youtube_credentials is True


def test_settings_fall_back_to_dummy_codex_file(tmp_path: Path) -> None:
    codex_env_file = tmp_path / ".env.codex"
    codex_env_file.write_text(
        "\n".join(
            [
                "SOUNDATLAS_USE_DUMMY_SERVICES=true",
                "YOUTUBE_API_KEY=dummy-youtube-key",
            ],
        ),
        encoding="utf-8",
    )

    settings = MediaEnrichmentSettings.from_env(
        env={},
        codex_env_file=codex_env_file,
    )

    assert settings.env_source == "codex"
    assert settings.use_dummy_services is True
    assert settings.has_live_youtube_credentials is False
