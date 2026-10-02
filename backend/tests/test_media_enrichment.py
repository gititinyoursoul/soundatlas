import gzip
import json
from pathlib import Path
from urllib.request import Request

import pytest

from app.config import PROJECT_ROOT
from app.media_enrichment import services
from app.media_enrichment.settings import MediaEnrichmentSettings, parse_env_file


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


def test_settings_load_application_root_with_process_overrides(tmp_path: Path) -> None:
    root = tmp_path / "external secrets"
    root.mkdir()
    (root / ".env").write_text(
        "YOUTUBE_API_KEY=file-dummy-key\nSOUNDATLAS_USE_DUMMY_SERVICES=false\n"
        "GH_TOKEN=repository-dummy-token\nGITHUB_TOKEN=another-dummy-token\n",
        encoding="utf-8",
    )
    settings = MediaEnrichmentSettings.from_env(
        env={
            "SOUNDATLAS_SECRETS_DIR": str(root),
            "YOUTUBE_API_KEY": "process-dummy-key",
            "SOUNDATLAS_USE_DUMMY_SERVICES": "true",
        },
    )
    assert settings.env_file == root / ".env"
    assert settings.env_source == "external"
    assert settings.youtube_api_key == "process-dummy-key"
    assert settings.use_dummy_services is True
    assert set(parse_env_file(root / ".env")) == {
        "YOUTUBE_API_KEY", "SOUNDATLAS_USE_DUMMY_SERVICES",
    }


def test_explicit_application_file_wins_over_invalid_root(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "mounted.env").write_text("YOUTUBE_API_KEY=dummy-mounted", encoding="utf-8")
    settings = MediaEnrichmentSettings.from_env(
        env={"SOUNDATLAS_ENV_FILE": "mounted.env", "SOUNDATLAS_SECRETS_DIR": "missing"},
    )
    assert settings.youtube_api_key == "dummy-mounted"
    assert settings.env_file == Path("mounted.env")


@pytest.mark.parametrize("kind", ["relative", "internal", "missing", "file"])
def test_invalid_application_root_does_not_fall_back(tmp_path: Path, kind: str) -> None:
    fallback = tmp_path / ".env.codex"
    fallback.write_text("YOUTUBE_API_KEY=dummy-fallback", encoding="utf-8")
    roots = {
        "relative": "relative/secrets",
        "internal": str(PROJECT_ROOT),
        "missing": str(tmp_path / "missing"),
        "file": str(fallback),
    }
    with pytest.raises(ValueError, match="SOUNDATLAS_SECRETS_DIR"):
        MediaEnrichmentSettings.from_env(
            env={"SOUNDATLAS_SECRETS_DIR": roots[kind], "YOUTUBE_API_KEY": "dummy-process"},
            codex_env_file=fallback,
        )


@pytest.mark.parametrize("selection", ["SOUNDATLAS_ENV_FILE", "SOUNDATLAS_SECRETS_DIR"])
@pytest.mark.parametrize("kind", ["missing", "directory", "invalid-text", "unreadable"])
def test_invalid_application_file_fails_safely(
    tmp_path: Path, monkeypatch, selection: str, kind: str,
) -> None:
    selected = tmp_path / ".env"
    if kind == "directory":
        selected.mkdir()
    elif kind == "invalid-text":
        selected.write_bytes(b"YOUTUBE_API_KEY=do-not-print\xff")
    elif kind == "unreadable":
        selected.touch()

        def denied(*args, **kwargs):
            raise PermissionError("do-not-print")

        monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(ValueError, match="Application credential file") as error:
        MediaEnrichmentSettings.from_env(
            env={selection: str(selected if selection == "SOUNDATLAS_ENV_FILE" else tmp_path)},
            codex_env_file=tmp_path / ".env.codex",
        )
    assert "do-not-print" not in str(error.value)


def test_invalid_explicit_file_does_not_use_valid_root(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("YOUTUBE_API_KEY=dummy-root", encoding="utf-8")
    with pytest.raises(ValueError, match="Application credential file"):
        MediaEnrichmentSettings.from_env(env={
            "SOUNDATLAS_ENV_FILE": str(tmp_path / "missing"),
            "SOUNDATLAS_SECRETS_DIR": str(tmp_path),
        })


def test_unconfigured_settings_remain_offline_without_github(tmp_path: Path) -> None:
    settings = MediaEnrichmentSettings.from_env(env={}, codex_env_file=tmp_path / "missing")
    assert settings.env_source == "none"
    assert settings.use_dummy_services is True
    assert settings.has_live_youtube_credentials is False


def test_empty_external_application_file_needs_no_github(tmp_path: Path) -> None:
    (tmp_path / ".env").touch()
    settings = MediaEnrichmentSettings.from_env(env={"SOUNDATLAS_SECRETS_DIR": str(tmp_path)})
    assert settings.env_source == "external"
    assert settings.has_live_youtube_credentials is False


def test_request_json_decompresses_gzip_responses(monkeypatch) -> None:
    payload = {"ok": True}
    compressed_body = gzip.compress(json.dumps(payload).encode("utf-8"))

    class FakeResponse:
        def __init__(self) -> None:
            self.headers = {"Content-Encoding": "gzip"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return compressed_body

    def fake_urlopen(request: Request, timeout: int = 30):
        return FakeResponse()

    monkeypatch.setattr(services.urllib.request, "urlopen", fake_urlopen)

    result = services.request_json("https://example.com/api")

    assert result == payload
