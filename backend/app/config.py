from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED_DIR = PROJECT_ROOT / "data" / "seed"
DEFAULT_CODEX_ENV_FILE = PROJECT_ROOT / ".env.codex"

LOCAL_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
