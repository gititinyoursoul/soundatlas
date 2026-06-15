import os
from dataclasses import dataclass
from pathlib import Path

from app.config import DEFAULT_CODEX_ENV_FILE


ALLOWED_ENV_KEYS = {
    "YOUTUBE_API_KEY",
    "SOUNDATLAS_USE_DUMMY_SERVICES",
}


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        normalized_key = key.strip()
        if normalized_key not in ALLOWED_ENV_KEYS:
            continue
        values[normalized_key] = value.strip().strip("\"'")
    return values


@dataclass(slots=True)
class MediaEnrichmentSettings:
    env_source: str
    env_file: Path | None
    use_dummy_services: bool
    youtube_api_key: str | None = None

    @classmethod
    def from_env(
        cls,
        env: dict[str, str] | None = None,
        codex_env_file: Path = DEFAULT_CODEX_ENV_FILE,
    ) -> "MediaEnrichmentSettings":
        env_values = dict(os.environ if env is None else env)
        env_file, env_source = resolve_env_file(env_values, codex_env_file)
        file_values = parse_env_file(env_file) if env_file else {}
        merged_values = file_values | {
            key: value
            for key, value in env_values.items()
            if key in ALLOWED_ENV_KEYS and value != ""
        }

        use_dummy_services = parse_bool(
            merged_values.get("SOUNDATLAS_USE_DUMMY_SERVICES"),
            default=env_source != "external",
        )
        return cls(
            env_source=env_source,
            env_file=env_file,
            use_dummy_services=use_dummy_services,
            youtube_api_key=merged_values.get("YOUTUBE_API_KEY") or None,
        )

    @property
    def has_live_youtube_credentials(self) -> bool:
        return bool(self.youtube_api_key) and not self.use_dummy_services


def resolve_env_file(
    env: dict[str, str],
    codex_env_file: Path = DEFAULT_CODEX_ENV_FILE,
) -> tuple[Path | None, str]:
    configured_path = env.get("SOUNDATLAS_ENV_FILE")
    if configured_path:
        env_file = Path(configured_path).expanduser()
        if not env_file.exists():
            raise ValueError(
                "SOUNDATLAS_ENV_FILE points to a missing file: "
                f"{env_file}",
            )
        return env_file, "external"
    if codex_env_file.exists():
        return codex_env_file, "codex"
    return None, "none"
