"""Opt-in Compose check for the non-root development-container contract.

Run only from a disposable checkout with SOUNDATLAS_CONTAINER_TEST_PROJECT set
to a unique project name. Volumes are retained across the recreation check.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

PROJECT = os.environ.get("SOUNDATLAS_CONTAINER_TEST_PROJECT")
REPO_ROOT = Path(__file__).resolve().parents[2]


def compose(*args: str) -> str:
    assert PROJECT is not None
    result = subprocess.run(
        ["docker", "compose", "--project-name", PROJECT, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def check_service(service: str, paths: tuple[str, ...]) -> None:
    if service == "backend":
        script = "\n".join(
            (
                "import os, pathlib, tempfile",
                "assert (os.getuid(), os.getgid()) == (10001, 10001)",
                "status = pathlib.Path('/proc/self/status').read_text()",
                "for key in ('CapPrm:', 'CapEff:', 'CapInh:', 'CapAmb:', 'CapBnd:'):",
                "    assert int(next(line.split()[1] for line in status.splitlines() if line.startswith(key)), 16) == 0",
                f"for item in {paths!r}:",
                "    path = pathlib.Path(item)",
                "    path.mkdir(parents=True, exist_ok=True)",
                "    with tempfile.NamedTemporaryFile(dir=path) as probe:",
                "        probe.write(b'ok')",
                "        probe.flush()",
                "        assert pathlib.Path(probe.name).read_bytes() == b'ok'",
            )
        )
        compose("exec", "-T", service, "python", "-c", script)
    else:
        node_script = (
            "const fs=require('fs'), os=require('os'), path=require('path');"
            "if(process.getuid()!=10001||process.getgid()!=10001)process.exit(1);"
            "const s=fs.readFileSync('/proc/self/status','utf8');"
            "for(const k of ['CapPrm','CapEff','CapInh','CapAmb','CapBnd']){"
            "const line=s.split('\\n').find(l=>l.startsWith(k+':'));"
            "if(BigInt('0x'+line.trim().split(/\\s+/)[1])!==0n)process.exit(2)}"
            f"for(const p of {list(paths)!r}){{"
            "fs.mkdirSync(p,{recursive:true});const f=path.join(p,'.soundatlas-startup-probe');"
            "fs.writeFileSync(f,'ok');if(fs.readFileSync(f,'utf8')!='ok')process.exit(3);fs.unlinkSync(f)}"
        )
        compose("exec", "-T", service, "node", "-e", node_script)


@pytest.mark.skipif(not PROJECT, reason="requires a unique disposable Compose project")
def test_non_root_startup_and_retained_writable_state() -> None:
    assert PROJECT is not None
    assert PROJECT.startswith("soundatlas272test"), "use a dedicated test project"
    backend_paths = (
        "/workspace/backend/.pytest_cache",
        "/workspace/backend/.ruff_cache",
        "/home/soundatlas/.cache/uv",
    )
    frontend_paths = (
        "/workspace/frontend/node_modules",
        "/workspace/frontend/.svelte-kit",
        "/workspace/frontend/build",
        "/workspace/frontend/static/soundatlas-data",
        "/workspace/frontend/screenshots",
        "/home/soundatlas/.npm",
    )
    try:
        compose("up", "-d", "--build", "--wait")
        for service, paths in (("backend", backend_paths), ("frontend", frontend_paths)):
            check_service(service, paths)
        compose("up", "-d", "--force-recreate", "--wait")
        for service, paths in (("backend", backend_paths), ("frontend", frontend_paths)):
            check_service(service, paths)
    finally:
        compose("down")  # Preserve the test volumes and any retained contents.
